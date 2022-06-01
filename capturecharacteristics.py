import asyncio
import sys
from bleak import BleakClient

temperature_uuid = "19b10000-2001-537e-4f6c-d104768a1214"
accelerometer_uuid = '19b10000-5001-537e-4f6c-d104768a1214'

def accelerometer_data_callback(handle, data):
  #print(handle, data)
  pass


async def main(address):
  async with BleakClient(address) as client:
    if (not client.is_connected):
      raise "client not connected"

    services = await client.get_services()
    await client.start_notify(accelerometer_uuid, accelerometer_data_callback)

    temp_bytes = await client.read_gatt_char(temperature_uuid)
    convert_temp_bytes_to_float(temp_bytes)

    await asyncio.sleep(60)
    await client.stop_notify(accelerometer_uuid)


def convert_temp_bytes_to_float(temp_bytes):
    temp_bytes = byte_array_to_int(temp_bytes)
    print( temp_bytes)

def byte_array_to_int(value):
    # Raw data is hexstring of int values, as a series of bytes, in little endian byte order
    # values are converted from bytes -> bytearray -> int
    # e.g., b'\xb8\x08\x00\x00' -> bytearray(b'\xb8\x08\x00\x00') -> 2232

    # print(f"{sys._getframe().f_code.co_name}: {value}")

    value = bytearray(value)
    value = int.from_bytes(value, byteorder="big")
    return value

if __name__ == "__main__":
    address = "42D1EB68-5EDF-85F9-D05E-82E0AD1CBD94"
    print('address:', address)
    asyncio.run(main(address))
