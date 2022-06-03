import asyncio
import sys
import struct
from bleak import BleakClient

sample_id_uuid = "19b10000-0001-537e-4f6c-d104768a1214" # 4 Byte float32
temperature_uuid = "19b10000-2001-537e-4f6c-d104768a1214" # 4 Byte float32
humidity_uuid = "19b10000-3001-537e-4f6c-d104768a1214" # 1 byte Uint8
accelerometer_uuid = "19b10000-5001-537e-4f6c-d104768a1214" # 3 times 4 byte float32 in an array
gyroscope_uuid = "19b10000-6001-537e-4f6c-d104768a1214" # 3 times 4 byte float32 in an array
quaternion_uuid = "19b10000-7001-537e-4f6c-d104768a1214" # 4 times 4 byte float32 in an array
pressure_uuid = "19b10000-4001-537e-4f6c-d104768a1214" # 4 times 4 byte float32 in an array
bundled_uuid = "19b10000-1002-537e-4f6c-d104768a1214" # Array of 11x 4 Bytes, AX,AY,AZ,GX,GY,GZ,QX,QY,QW,QZ,P

def sample_id_callback(handle, data):
    #print(handle, data)
    [sample_id] = struct.unpack('f', data)
    #print(f"ID: {sample_id}")

def gyroscope_data_callback(handle, data):
    # print(handle, data)
    [x,y,z] = struct.unpack('fff', data)
    #print(f"{x}, {y}, {z}")

def quaternation_data_callback(handle, data):
    # print(handle, data)
    [x,y,z,w] = struct.unpack('ffff', data)

def accelerometer_data_callback(handle, data):
    # print(handle, data)
    [Ax,Ay,Az] = struct.unpack('fff', data)
    #print(Ax)

def pressure_data_callback(handle, data):
    # print(handle, data)
    [pressure] = struct.unpack('f', data)
    #print(pressure)

def bundle_callback(handle, data):
    #print(handle, data)
    [ax,ay,az,gx,gy,gz,qx,qy,qz,qw,p] = struct.unpack('fffffffffff', data)
    print(f"{ax}, {ay}, {az}, {gx}, {gy}, {gz}, {qx}, {qy}, {qz}, {qw}, {p}")

async def main(address):
    async with BleakClient(address) as client:
        if (not client.is_connected):
            raise "client not connected"

        services = await client.get_services()
        await client.start_notify(sample_id_uuid, sample_id_callback)
        await client.start_notify(accelerometer_uuid, accelerometer_data_callback)
        await client.start_notify(gyroscope_uuid, gyroscope_data_callback)
        await client.start_notify(quaternion_uuid, quaternation_data_callback)
        await client.start_notify(pressure_uuid, pressure_data_callback)
        await client.start_notify(bundled_uuid, bundle_callback)
        #temp_bytes = await client.read_gatt_char(temperature_uuid)         #print(hexlify(temp_bytes))
        #[temperature] = struct.unpack('f', temp_bytes)
        #print(temperature)

        #humidity_bytes = await client.read_gatt_char(humidity_uuid)
        #[humidity] = struct.unpack('i', humidity_bytes)
        #print(humidity)

        await asyncio.sleep(6000000)
        await client.stop_notify(accelerometer_uuid)

if __name__ == "__main__":
    address = "02D307CC-39AB-9D1B-A279-6B8245193D28"
    print('address:', address)
    asyncio.run(main(address))
