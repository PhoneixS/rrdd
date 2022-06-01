import asyncio
import logging
from bleak import BleakScanner, BleakClient


logger = logging.getLogger(__name__)

RRDD_ADDRESS = "EF:3A:A4:C3:77:8B"

async def list_devices():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)
        if d.name == "2ndHeroD":
            print("Encontrado R2D2")

async def main():

    await list_devices()

    async with BleakClient(RRDD_ADDRESS) as client:

        logger.info(f"Connected: {client.is_connected}")
        
        for service in client.services:
            logger.info(f"[Service] {service}")
            for char in service.characteristics:
                if "read" in char.properties:
                    try:
                        value = bytes(await client.read_gatt_char(char.uuid))
                        logger.info(
                            f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {value}"
                        )
                    except Exception as e:
                        logger.error(
                            f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {e}"
                        )

                else:
                    value = None
                    logger.info(
                        f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {value}"
                    )

                for descriptor in char.descriptors:
                    try:
                        value = bytes(
                            await client.read_gatt_descriptor(descriptor.handle)
                        )
                        logger.info(f"\t\t[Descriptor] {descriptor}) | Value: {value}")
                    except Exception as e:
                        logger.error(f"\t\t[Descriptor] {descriptor}) | Value: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())