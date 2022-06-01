
import logging

from bleak.backends.device import BLEDevice
from bleak import BleakScanner, BleakClient
from soupsieve import match

logger = logging.getLogger(__name__)


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
        
    def process_ir_data(self, data: bytearray) -> None:
        logger.info(f"IR data received: {data.hex(sep=':')}")
    
    def process_mic_event(self, data: bytearray) -> None:
        logger.info(f"Mic event received: {data.hex(sep=':')}")
    
    def radio_data_received(self, sender: int, data: bytearray) -> None:
        logger.info(f"Radio data received: {data.hex(sep=':')}")


    async def start_drive_mode(self) -> None:

        if self.client is None or not self.client.is_connected:
            await self.client.connect()

        data = bytearray(b'\x19\x01')
        await self.client.write_gatt_char(self.DATA_WRITE_UUID, data)