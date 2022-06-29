# Github Repo with code for training the AI model and acquiring all sensor values from the Nicla Sense ME

To install the necessary python requirements do:
```
pip install -r requirements.txt
```

To execute the Backend with the machine learning model:
```
python3 keeprunning.py
```
Keep in mind to replace the 
```
address = "Your device UUID"
```
at the end of the file `capturecharacteristics.py (Lines 245 onwards)`
with the UUID of your device.
If the UUID is unknown to you, execute the file
```
python3 util/scan_for_nearby_ble_devices.py
```

To execute the Frontend with the machine learning model:
```
python3 dashboard/plotly_dash_start.py
```
You have to start two terminal windows/tabs to let both processes run at the same time.