import struct
from threading import Thread
import requests
import json

temperature_uuid = "19b10000-2001-537e-4f6c-d104768a1214"  # 4 Byte float32
humidity_uuid = "19b10000-3001-537e-4f6c-d104768a1214"  # 1 byte Uint8


async def execute_device_heartbeat(client):
    print("Executing Device Status Update")
    temp_bytes = await client.read_gatt_char(temperature_uuid)  # print(hexlify(temp_bytes))
    [temperature] = struct.unpack('f', temp_bytes)
    calibrated_temp = 1.0095 * temperature - 6.8051
    print("Temperature at the moment:" + str(calibrated_temp))

    humidity_bytes = await client.read_gatt_char(humidity_uuid)
    [humidity] = struct.unpack('I', humidity_bytes)
    calibrated_humidity = 1.4383 * humidity - 2.5628
    print("Humidity at the moment:" + str(calibrated_humidity))
    execute_request_thread = Thread(target=send_device_heartbeat_request,
                                    args=(calibrated_temp, calibrated_humidity))
    execute_request_thread.start()


def send_device_heartbeat_request(temperature, humidity):
    url = "https://europe-west1-erudite-visitor-336410.cloudfunctions.net/updateDeviceState"

    payload = json.dumps({
        "deviceId": "did_0001",
        "batteryLevel": 100,
        "temperature": temperature,
        "humidity": humidity
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print("Response form Heartbeat Request:" + str(response.text))
