import asyncio
import struct
from bleak import BleakClient
import websockets
import json
import pandas as pd
from websockets.legacy.server import WebSocketServer

CLIENTS = set()


sample_dict_list = []
sample_count_int: int = 0
startcapture: bool = False
liveTransmit: bool = False

sample_id_uuid = "19b10000-0001-537e-4f6c-d104768a1214" # 4 Byte float32
temperature_uuid = "19b10000-2001-537e-4f6c-d104768a1214" # 4 Byte float32
humidity_uuid = "19b10000-3001-537e-4f6c-d104768a1214" # 1 byte Uint8
accelerometer_uuid = "19b10000-5001-537e-4f6c-d104768a1214" # 3 times 4 byte float32 in an array
gyroscope_uuid = "19b10000-6001-537e-4f6c-d104768a1214" # 3 times 4 byte float32 in an array
quaternion_uuid = "19b10000-7001-537e-4f6c-d104768a1214" # 4 times 4 byte float32 in an array
pressure_uuid = "19b10000-4001-537e-4f6c-d104768a1214" # 4 times 4 byte float32 in an array
bundled_uuid = "19b10000-1002-537e-4f6c-d104768a1214" # Array of 11x 4 Bytes, AX,AY,AZ,GX,GY,GZ,QX,QY,QW,QZ,P

def sample_id_callback(handle, data):
    # print(handle, data)
    [sample_id] = struct.unpack('f', data)
    # print(f"ID: {sample_id}")


def gyroscope_data_callback(handle, data):
    # print(handle, data)
    [x, y, z] = struct.unpack('fff', data)
    # print(f"{x}, {y}, {z}")


def quaternation_data_callback(handle, data):
    # print(handle, data)
    [x, y, z, w] = struct.unpack('ffff', data)


def accelerometer_data_callback(handle, data):
    # print(handle, data)
    [Ax, Ay, Az] = struct.unpack('fff', data)
    # print(Ax)


def pressure_data_callback(handle, data):
    # print(handle, data)
    [pressure] = struct.unpack('f', data)

    # print(pressure)


def bundle_callback(handle, data):
    # print(handle, data)
    [ax, ay, az, gx, gy, gz, qx, qy, qz, qw, p] = struct.unpack('fffffffffff', data)
    # asyncio.create_task(broadcastMessage(f"New Values came in: {ax}"))
    global sample_count_int
    global startcapture
    global sample_dict_list
    if startcapture:
        sample_count_int +=1
        sample_dict = {"ax": ax, "ay": ay, "az": az, "gx": gx, "gy": gy, "gz": gz, "qx": qx, "qy": qy, "qz": qz,
                       "qw": qw, "p": p}
        sample_dict_list.append(sample_dict)
        print(sample_count_int)
        if sample_count_int == 200:
            startcapture = False
            sample_count_int = 0
            sample_df = pd.DataFrame(sample_dict_list)
            sample_df.to_csv("./data/test.csv", sep=',', index=False)
            result = sample_df.to_json(orient="index")
            sample_dict_list = []
            asyncio.create_task(broadcastMessage("dataframeoutput:" + result))
            print(result)

        print(f"{ax}, {ay}, {az}, {gx}, {gy}, {gz}, {qx}, {qy}, {qz}, {qw}, {p}")
    if liveTransmit:
        sample_dict = {"ax": ax, "ay": ay, "az": az, "gx": gx, "gy": gy, "gz": gz, "qx": qx, "qy": qy, "qz": qz,
                       "qw": qw, "p": p}
        asyncio.create_task(broadcastMessage("liveData:" + json.dumps(sample_dict)))



def disconnected_callback(client):
    print("Client with address {} got disconnected!".format(client.address))
    quit()

async def main(address):
    async with BleakClient(address) as client:
        if (not client.is_connected):
            raise "client not connected"

        #services = await client.get_services()
        await client.start_notify(sample_id_uuid, sample_id_callback)
        await client.start_notify(accelerometer_uuid, accelerometer_data_callback)
        await client.start_notify(gyroscope_uuid, gyroscope_data_callback)
        await client.start_notify(quaternion_uuid, quaternation_data_callback)
        await client.start_notify(pressure_uuid, pressure_data_callback)
        await client.start_notify(bundled_uuid, bundle_callback)
        client.set_disconnected_callback(disconnected_callback)
        # temp_bytes = await client.read_gatt_char(temperature_uuid)         #print(hexlify(temp_bytes))
        # [temperature] = struct.unpack('f', temp_bytes)
        # print(temperature)

        # humidity_bytes = await client.read_gatt_char(humidity_uuid)
        # [humidity] = struct.unpack('i', humidity_bytes)
        # print(humidity)
        async with websockets.serve(handler, "0.0.0.0", 5300) as websocket:
            await asyncio.Future()  # run forever
        #await client.stop_notify(accelerometer_uuid)


async def broadcastMessage(msg):
        for ws in CLIENTS:
            try:
                await ws.send(msg)
            except websockets.ConnectionClosed:
                pass


async def handler(websocket):
    global liveTransmit
    CLIENTS.add(websocket)
    try:
        async for msg in websocket:
            if msg == "start":
                global startcapture
                startcapture = True
                print("StartCapture state:" + str(startcapture))
            if msg == "live":
                liveTransmit = True
                print("LiveTransmit state:" + str(liveTransmit))
            if msg == "stopLive":
                liveTransmit = False
                print("LiveTransmit state:" + str(liveTransmit))
            await websocket.send(msg)
            pass
    finally:
        CLIENTS.remove(websocket)


if __name__ == "__main__":
    address = "02D307CC-39AB-9D1B-A279-6B8245193D28"
    address = "42D1EB68-5EDF-85F9-D05E-82E0AD1CBD94"
    print('address:', address)
    asyncio.run(main(address))
