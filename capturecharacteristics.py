import asyncio
import sys
from bleak import BleakClient

temperature_uuid = "19b10000-2001-537e-4f6c-d104768a1214"

async def main(address):
  async with BleakClient(address) as client:
    if (not client.is_connected):
      raise "client not connected"

    services = await client.get_services()

    temp_bytes = await client.read_gatt_char(temperature_uuid)
    print( temp_bytes)


if __name__ == "__main__":
    address = "42D1EB68-5EDF-85F9-D05E-82E0AD1CBD94"
    print('address:', address)
    asyncio.run(main(address))
