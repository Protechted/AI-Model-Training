import asyncio
import sys
import struct
from bleak import BleakClient
from binascii import hexlify

temperature_uuid = "19b10000-2001-537e-4f6c-d104768a1214" # 4 Byte float32
humidity_uuid = "19b10000-3001-537e-4f6c-d104768a1214" # 1 byte Uint8
accelerometer_uuid = "19b10000-5001-537e-4f6c-d104768a1214" # 3 times 4 byte float32 in an array
gyroscope_uuid = "19b10000-6001-537e-4f6c-d104768a1214" # 3 times 2 byte Uint16 in an array
quaternion_uuid = "19b10000-7001-537e-4f6c-d104768a1214" # 4 times 4 byte float32 in an array


def gyroscope_data_callback(handle, data):
    # print(handle, data)
    [x,y,z] = struct.unpack('HHH', data)
    #print(x)

    pass
def quaternation_data_callback(handle, data):
    # print(handle, data)
    [x,y,z,w] = struct.unpack('ffff', data)
    print(x)

def accelerometer_data_callback(handle, data):
    # print(handle, data)
    [Ax,Ay,Az] = struct.unpack('fff', data)
    #print(Ax)


async def main(address):
    async with BleakClient(address) as client:
        if (not client.is_connected):
            raise "client not connected"

        services = await client.get_services()
        await client.start_notify(accelerometer_uuid, accelerometer_data_callback)
        await client.start_notify(gyroscope_uuid, gyroscope_data_callback)
        await client.start_notify(quaternion_uuid, quaternation_data_callback)



        temp_bytes = await client.read_gatt_char(temperature_uuid)         #print(hexlify(temp_bytes))
        [temperature] = struct.unpack('f', temp_bytes)
        print(temperature)

        humidity_bytes = await client.read_gatt_char(humidity_uuid)
        [humidity] = struct.unpack('i', humidity_bytes)
        print(humidity)


        await asyncio.sleep(6000000)
        await client.stop_notify(accelerometer_uuid)


def indef_loop():
    while (True):
        pass

def byte_array_to_int(value):
    value = bytearray(value)
    value = int.from_bytes(value, byteorder="little")
    return value


if __name__ == "__main__":
    address = "42D1EB68-5EDF-85F9-D05E-82E0AD1CBD94"
    print('address:', address)
    asyncio.run(main(address))
