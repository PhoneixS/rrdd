
from enum import Enum
import logging

from bleak.backends.device import BLEDevice
from bleak import BleakScanner, BleakClient

logger = logging.getLogger(__name__)

class DialPosition(Enum):
    INVALID = 0
    RIGHT = 1
    LEFT = 2
    CENTER = 3

class HeadPosition(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2

class EventListener():
    '''This class represent an event listener that you can add to run code when an event happens'''

    def on_button_state_change(self, button_pressed: bool):
        pass

    def on_dial_position_change(self, dial_position: DialPosition):
        pass

    def on_head_position_change(self, head_position: HeadPosition):
        pass
        
    def on_cam_grey_code_change(self, cam_grey_code: int):
        pass

def data_to_dial_position(data) -> DialPosition:
    return DialPosition((data >> 3) & 3)

def data_to_button_pressed(data) -> bool:
    return (data & 1) == 1

def data_to_head_position(data) -> HeadPosition:
    match (data >> 7) & 3:
        case 0:
            return HeadPosition.RIGHT
        case 1:
            return HeadPosition.LEFT
        case _:
            return HeadPosition.CENTER

def data_to_cam_grey_code(data) -> int:
    return (data >> 3) & 0xF

class Rrdd:

    DEFAULT_NAME = "2ndHeroD"
    DEFAULT_ADDRESS = "EF:3A:A4:C3:77:8B"
    DATA_RECEIVED_UUID = "DAB91382-B5A1-E29C-B041-BCD562613BE4"
    DATA_WRITE_UUID = "DAB91383-B5A1-E29C-B041-BCD562613BE4"
    RADIO_DATA_RECEIVED_UUID = "DAB90756-B5A1-E29C-B041-BCD562613BE4"
    RADIO_DATA_WRITE_UUID = "DAB90757-B5A1-E29C-B041-BCD562613BE4"
    
    def __init__(self) -> None:
        self.client = None
        self.device = None

        self._previous_dial_position = DialPosition(0)
        self._previous_button_pressed = False
        self._previous_head_position = HeadPosition(0)
        self._previous_cam_grey_code = 0

        self._event_listeners = []
    
    async def searchDevice(self, name: str = None) -> None:
        if name is None:
            name = self.DEFAULT_NAME
        
        # Search for the correct device
        self.device = await BleakScanner.find_device_by_filter(filterfunc=lambda dv,da: dv.name == self.DEFAULT_NAME)

    async def connect(self) -> bool:
        if self.device is None:
            raise ConnectionError("Device not set")
        
        if self.client is not None and self.client.is_connected:
            return True

        self.client = BleakClient(self.device)
        await self.client.connect()

        await self.client.start_notify(self.DATA_RECEIVED_UUID, self.data_received)
        await self.client.start_notify(self.RADIO_DATA_RECEIVED_UUID, self.radio_data_received)

        return True
    
    def data_received(self, sender: int, data: bytearray) -> None:
        
        if not data:
            return
        
        match data[0]:
            case 16:
                self.process_playlist_end_message(data)
            case 22:
                self.process_ir_data(data)
            case 27:
                self.process_mic_event(data)
            case 23:
                self.process_sequence_end_message(data)
            case 32:
                self.process_toy_input_message(int.from_bytes(data[1:3], 'little'))
            case 96 | 97 | 98:
                logger.info(f"Unknown bluetooth message received: {data.decode(encoding='ascii')}")
            case _:
                logger.info(f"Unknown data received: {data.hex(sep=':')}")
    
    def process_playlist_end_message(self, data: bytearray) -> None:
        logger.info(f"Playlist end data received: {data.hex(sep=':')}")

    def process_sequence_end_message(self, data: bytearray) -> None:
        logger.info(f"Sequence end data received: {data.hex(sep=':')}")

    def process_toy_input_message(self, data: int) -> None:

        logger.info(f"Toy input data received: {data}")

        dial_position = data_to_dial_position(data)
        button_pressed = data_to_button_pressed(data)
        head_position = data_to_head_position(data)
        cam_grey_code = data_to_cam_grey_code(data)

        if button_pressed != self._previous_button_pressed:
            self.on_button_state_change(button_pressed)
        
        if dial_position != self._previous_dial_position:
            self.on_dial_position_change(dial_position)

        if head_position != self._previous_head_position:
            self.on_head_position_change(head_position)
        
        if cam_grey_code != self._previous_cam_grey_code:
            self.on_cam_grey_code_change(cam_grey_code)
        
        self._previous_dial_position = dial_position
        self._previous_button_pressed = button_pressed
        self._previous_head_position = head_position
        self._previous_cam_grey_code = cam_grey_code
        
        
    def process_ir_data(self, data: bytearray) -> None:
        logger.debug(f"IR data received: {data.hex(sep=':')}")
        # TODO Process IR data
    
    def process_mic_event(self, data: bytearray) -> None:
        logger.debug(f"Mic event received: {data.hex(sep=':')}")
        # TODO Process mic event
    
    def radio_data_received(self, sender: int, data: bytearray) -> None:
        logger.debug(f"Radio data received: {data.hex(sep=':')}")
        # TODO Process radio data


    async def start_drive_mode(self) -> None:

        if self.client is None or not self.client.is_connected:
            await self.client.connect()

        data = bytearray(b'\x19\x01')
        await self.client.write_gatt_char(self.DATA_WRITE_UUID, data)
    
    def on_button_state_change(self, button_pressed: bool):
        logger.info(f"Button pressed changed to {button_pressed}")
        for listener in self._event_listeners:
            listener.on_button_state_change(button_pressed)

    def on_dial_position_change(self, dial_position: DialPosition):
        logger.info(f"Dial position changed to {dial_position}")
        for listener in self._event_listeners:
            listener.on_dial_position_change(dial_position)

    def on_head_position_change(self, head_position: HeadPosition):
        logger.info(f"Head position changed to {head_position}")
        for listener in self._event_listeners:
            listener.on_head_position_change(head_position)
        
    def on_cam_grey_code_change(self, cam_grey_code: int):
        logger.info(f"Cam grey code changed to {cam_grey_code}")
        for listener in self._event_listeners:
            listener.on_cam_grey_code_change(cam_grey_code)
    
    def add_listener(self, listener):
        self._event_listeners.append(listener)
    
    def remove_listener(self, listener):
        self._event_listeners.remove(listener)