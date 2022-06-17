import asyncio
import struct
from collections import deque
from tabnanny import verbose
from threading import Thread
from typing import Deque, List
from util.send_fall_detected_request import execute_fall_detected_request
from util.list_util import average_of_list
from util.send_device_status import execute_device_heartbeat
from callbacks import *
from tensorflow_addons.metrics import F1Score


from bleak import BleakClient
#import pickle
#import xgboost as xgb
import datetime
import websockets
import json
import pandas as pd
import tensorflow as tf
import numpy as np

CLIENTS = set()

sample_dict_list: List[dict] = []
sample_count_int: int = 0
startcapture: bool = False

startcapturecontinous: bool = False
sample_count_continous_int: int = 0
sample_dict_list_continous: List[dict] = []

liveTransmit: bool = False  # Is controlled via the dashboard, enables live data transmission over the websocket
live_transmit_counter = 0
modelaction: bool = True  # Enables the live ML-Model prediction
sendNotifications: bool = False  # Enables the sending of emergency Notifications to the Backend
enableDeviceHeartbeat: bool = True # Enables a periodic sending of device information, 60s interval

collected_data: Deque[dict] = deque(maxlen=150)
moving_window_tick_counter: int = 0

last_x_probabilities: Deque[float] = deque(maxlen=100)
averaging_tick_counter: int = 0

sample_id_uuid = "19b10000-0001-537e-4f6c-d104768a1214" # 4 Byte float32
accelerometer_uuid = "19b10000-5001-537e-4f6c-d104768a1214" # 3 times 4 byte float32 in an array
gyroscope_uuid = "19b10000-6001-537e-4f6c-d104768a1214" # 3 times 4 byte float32 in an array
quaternion_uuid = "19b10000-7001-537e-4f6c-d104768a1214" # 4 times 4 byte float32 in an array
pressure_uuid = "19b10000-4001-537e-4f6c-d104768a1214" # 4 times 4 byte float32 in an array
bundled_uuid = "19b10000-1002-537e-4f6c-d104768a1214" # Array of 11x 4 Bytes, AX,AY,AZ,GX,GY,GZ,QX,QY,QW,QZ,P


#model = xgb.Booster(model_file="./models/xgb_model_1.bin")
# predict the test data
model = tf.keras.models.load_model("./models/gru_classifier_1.h5")
#model = pickle.load(open("models/naive_bayes.sav", 'rb'))

def model_predict(collected_data: List[dict], mlmodel, last_x_probabilities: Deque[float]):
    #print("test model predict")
    collected_data = [list(sample.values()) for sample in collected_data]
    collected_data = np.array(collected_data)
    probability = mlmodel.predict(np.expand_dims(collected_data, axis=0), verbose=0)[0][0]
    # flatten the array (if necessary)
    #collected_data = collected_data.reshape(collected_data.shape[0] * collected_data.shape[1])
    #probability = mlmodel.predict(np.expand_dims(collected_data,0))
    #probability = mlmodel.predict(xgb.DMatrix(np.expand_dims(collected_data,0)))
    last_x_probabilities.append(probability)
    #print(probability)

def bundle_callback(handle, data):
    # print(handle, data)
    [ax, ay, az, gx, gy, gz, qx, qy, qz, qw, p] = struct.unpack('fffffffffff', data)
    # asyncio.create_task(broadcastMessage(f"New Values came in: {ax}"))
    sample_dict = {"ax": ax, "ay": ay, "az": az, "gx": gx, "gy": gy, "gz": gz, "qx": qx, "qy": qy, "qz": qz,
                   "qw": qw, "p": p}
    global sample_count_int
    global startcapture
    global liveTransmit
    global modelaction
    global sample_dict_list
    global collected_data
    global moving_window_tick_counter
    global last_x_probabilities
    global averaging_tick_counter
    global live_transmit_counter

    if modelaction:
        collected_data.append(sample_dict)
        moving_window_tick_counter += 1
        if moving_window_tick_counter > 200:
            if moving_window_tick_counter % 2 == 0:
                thread = Thread(target=model_predict, args=(list(collected_data), model, last_x_probabilities))
                thread.start()
                averaging_tick_counter += 1
                if averaging_tick_counter == 20:
                    averageprob: float = average_of_list(last_x_probabilities)
                    print("AverageProbability: " + str(averageprob))
                    if averageprob >= 0.90:
                        if sendNotifications:
                            timestamp: str = datetime.datetime.now().isoformat()
                            print("Executing Emergency REST call at " + timestamp + "with a probability of: " + str(
                                averageprob))
                            execute_request_thread = Thread(target=execute_fall_detected_request,
                                                            args=(timestamp, averageprob))
                            execute_request_thread.start()

                    averaging_tick_counter = 0

    if startcapture:
        sample_count_int += 1

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

    if startcapturecontinous:
        global sample_count_continous_int
        global sample_dict_list_continous
        sample_count_continous_int += 1
        sample_dict_list_continous.append(sample_dict)
        if (sample_count_continous_int == 200):
            sample_count_continous_int = 0
            sample_df = pd.DataFrame(sample_dict_list_continous)
            result = sample_df.to_json(orient="index")
            asyncio.create_task(broadcastMessage("dataframeoutputcontinous:" + result))
            sample_dict_list_continous = []
            print("Sent Continous Sample of 200 Ticks")

    if liveTransmit:
        if live_transmit_counter == 4:
            asyncio.create_task(broadcastMessage("liveData:" + json.dumps(sample_dict)))
            live_transmit_counter = 0
        else:
            live_transmit_counter += 1


def disconnected_callback(client):
    print("Client with address {} got disconnected!".format(client.address))
    quit()


async def main(address):
    async with BleakClient(address) as client:
        if (not client.is_connected):
            raise "client not connected"

        # services = await client.get_services()
        await client.start_notify(sample_id_uuid, sample_id_callback)
        await client.start_notify(accelerometer_uuid, accelerometer_data_callback)
        await client.start_notify(gyroscope_uuid, gyroscope_data_callback)
        await client.start_notify(quaternion_uuid, quaternation_data_callback)
        await client.start_notify(pressure_uuid, pressure_data_callback)
        await client.start_notify(bundled_uuid, bundle_callback)
        client.set_disconnected_callback(disconnected_callback)

        async with websockets.serve(handler, "0.0.0.0", 5300) as websocket:
            if enableDeviceHeartbeat:
                while True:
                    await asyncio.gather(
                        asyncio.sleep(60),
                        execute_device_heartbeat(client=client),
                    )
            await asyncio.Future()  # run forever
        await asyncio.Future() # In case the Websocket crashes, the application should still run, the websocket is not essential for production
        # await client.stop_notify(accelerometer_uuid)


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
            if msg == "startcontinoustraining":
                global startcapturecontinous
                startcapturecontinous = True
                print("StartCaptureContinous state for continous Training:" + str(startcapturecontinous))
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
    #address = "42D1EB68-5EDF-85F9-D05E-82E0AD1CBD94"
    print('address:', address)
    asyncio.run(main(address))
