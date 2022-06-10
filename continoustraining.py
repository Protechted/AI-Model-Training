import asyncio
import websockets
import pandas as pd
from dashboard.insert import insert_data


async def run_websocket():
    async with websockets.connect(
            'ws://localhost:5300') as websocket:
        await websocket.send("startcontinoustraining")
        print("Sent Continous Training request to websocket server")

        while True:
            answer = await websocket.recv()
            print("Received from websocket: "+ answer)
            if str(answer) == None:
                return
            if str(answer).startswith("dataframeoutputcontinous:"):
                dataframe_string = str(answer).split("dataframeoutputcontinous:")[1]
                loaded_df = pd.read_json(dataframe_string, orient='index')
                print(loaded_df)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run_websocket())
