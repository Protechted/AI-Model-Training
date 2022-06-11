import requests
import json

def execute_fall_detected_request(timestamp: str, probability: float):
    url = "https://europe-west1-erudite-visitor-336410.cloudfunctions.net/emergency"

    payload = json.dumps({
        "deviceId": "did_0001",
        "code": 10,
        "timestamp": timestamp,
        "probability": str(probability)
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
