import asyncio
from threading import Thread
import websockets
import pandas as pd
from dashboard.insert import insert_data
import signal
import sys

stop_bool: bool = True

def signal_handler(sig, frame):
    global stop_bool
    stop_bool = False
    print('You pressed Ctrl+C!')

async def run_websocket():
    global stop_bool

    async with websockets.connect(
            'ws://localhost:5300') as websocket:
        await websocket.send("startcontinoustraining")
        print("Sent Continous Training request to websocket server")

        while stop_bool:
            answer = await websocket.recv()
            print("Received from websocket: "+ answer)
            if str(answer) == None:
                return
            if str(answer).startswith("dataframeoutputcontinous:"):
                dataframe_string = str(answer).split("dataframeoutputcontinous:")[1]
                loaded_df = pd.read_json(dataframe_string, orient='index')
                thread = Thread(target=insert_data, args=(loaded_df, "D4", "HandLiegtAufTischMitRotation"))
                thread.start()
                print("Inserted Continous Training Data")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    asyncio.get_event_loop().run_until_complete(run_websocket())
