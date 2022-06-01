import asyncio
import logging
import sys
from bleak import BleakScanner, BleakClient

from rrdd import Rrdd


logger = logging.getLogger(__name__)

RRDD_ADDRESS = "EF:3A:A4:C3:77:8B"
RRDD_ServiceUUID = "DAB91435-B5A1-E29C-B041-BCD562613BE4"
RRDD_SubscribeCharacteristic = "DAB91382-B5A1-E29C-B041-BCD562613BE4"
RRDD_WriteCharacteristic = "DAB91383-B5A1-E29C-B041-BCD562613BE4"
RRDD_RadioSubCharacteristic = "DAB90756-B5A1-E29C-B041-BCD562613BE4"
RRDD_RadioWriteCharacteristic = "DAB90757-B5A1-E29C-B041-BCD562613BE4"

async def ainput(string: str) -> str:
    await asyncio.get_event_loop().run_in_executor(
            None, lambda s=string: sys.stdout.write(s+' '))
    return await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline)

async def main():

    # async with BleakClient(RRDD_ADDRESS) as client:

    #     logger.info(f"Connected: {client.is_connected}")
        
        
    #     sendSrv = client.services.get_service("DAB91435-B5A1-E29C-B041-BCD562613BE4")
    #     sendChr = sendSrv.get_characteristic("DAB91383-B5A1-E29C-B041-BCD562613BE4")
    #     logger.info(f"Starting send")
    #     await client.write_gatt_char(sendChr, [19, 1])
    #     logger.info(f"Sent: 19 1")
    #     await client.write_gatt_char(sendChr, [19, 0])
    #     logger.info(f"Sent: 19 0")
    #     await client.write_gatt_char(sendChr, [19, 1])
    #     logger.info(f"Sent: 19 1")

    rrdd = Rrdd()
    logger.info("searching device...")
    await rrdd.searchDevice()
    logger.info("connecting to device...")
    await rrdd.connect()
    logger.info("starting drive mode...")
    await rrdd.start_drive_mode()
    logger.info("nothing more to do, waiting 60 seconds")
    
    await ainput("Pulsa intro para salir")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())