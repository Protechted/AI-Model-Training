/*

  Arduino Nicla Sense ME WEB Bluetooth® Low Energy Sense dashboard demo


  Hardware required: https://store.arduino.cc/nicla-sense-me

  1) Upload this sketch to the Arduino Nano BLE sense board

  2) Open the following web page in the Chrome browser:
  https://arduino.github.io/ArduinoAI/NiclaSenseME-dashboard/

  3) Click on the green button in the web page to connect the browser to the board over Bluetooth® Low Energy


  Web dashboard by D. Pajak

  Device sketch based on example by Sandeep Mistry and Massimo Banzi
  Sketch and web dashboard copy-fixed to be used with the Nicla Sense ME by Pablo Marquínez

  */

  #include "Nicla_System.h"
  #include "Arduino_BHY2.h"
  #include <ArduinoBLE.h>

  #define BLE_SENSE_UUID(val) ("19b10000" val "-537e-4f6c-d104768a1214")
  #define NUM_AXES 3
  double baseline_a[NUM_AXES];
  double baseline_g[NUM_AXES];

  const int VERSION = 0x00000000;

  const float accelerationThreshold = 1.0; // threshold of significant in G's
  const int numSamples = 100;
  int truncate = 25000.0;

  int samplesRead = numSamples;

  float randNumber;

  BLEService service(BLE_SENSE_UUID("0000"));

  BLEFloatCharacteristic sampleIdCharacteristic(BLE_SENSE_UUID("0001"), BLENotify);
  BLEUnsignedIntCharacteristic versionCharacteristic(BLE_SENSE_UUID("1001"), BLERead);
  BLEFloatCharacteristic temperatureCharacteristic(BLE_SENSE_UUID("2001"), BLERead);
  BLEUnsignedIntCharacteristic humidityCharacteristic(BLE_SENSE_UUID("3001"), BLERead);
  BLEFloatCharacteristic pressureCharacteristic(BLE_SENSE_UUID("4001"), BLERead);


  BLECharacteristic accelerometerCharacteristic(BLE_SENSE_UUID("5001"), BLERead | BLENotify, 3 * sizeof(float));  // Array of 3x 2 Bytes, XY
  BLECharacteristic gyroscopeCharacteristic(BLE_SENSE_UUID("6001"), BLERead | BLENotify, 3 * sizeof(float));    // Array of 3x 2 Bytes, XYZ
  BLECharacteristic quaternionCharacteristic(BLE_SENSE_UUID("7001"), BLERead | BLENotify, 4 * sizeof(float));     // Array of 4x 2 Bytes, XYZW
  

  BLECharacteristic rgbLedCharacteristic(BLE_SENSE_UUID("8001"), BLERead | BLEWrite, 3 * sizeof(byte)); // Array of 3 bytes, RGB
  BLEFloatCharacteristic bsecCharacteristic(BLE_SENSE_UUID("9001"), BLERead);
  BLEIntCharacteristic  co2Characteristic(BLE_SENSE_UUID("9002"), BLERead);
  BLEUnsignedIntCharacteristic gasCharacteristic(BLE_SENSE_UUID("9003"), BLERead); 



  // String to calculate the local and device name
  String name;

  Sensor temperature(SENSOR_ID_TEMP);
  Sensor humidity(SENSOR_ID_HUM);
  Sensor pressure(SENSOR_ID_BARO);
  Sensor gas(SENSOR_ID_GAS);
  SensorXYZ gyroscope(SENSOR_ID_GYRO);
  SensorXYZ accelerometer(SENSOR_ID_ACC);
  SensorQuaternion quaternion(SENSOR_ID_RV);
  SensorBSEC bsec(SENSOR_ID_BSEC);

  void setup(){
    Serial.begin(9600);

    Serial.println("Start");

    nicla::begin();
    nicla::leds.begin();
    nicla::leds.setColor(green);

    //Sensors initialization
    BHY2.begin();
    temperature.begin();
    humidity.begin();
    pressure.begin();
    gyroscope.begin();
    accelerometer.begin();
    quaternion.begin();
    bsec.begin();
    gas.begin();

    if (!BLE.begin()){
      Serial.println("Failed to initialized Bluetooth® Low Energy!");

      while (1)
        ;
    }


    String address = BLE.address();

    Serial.print("address = ");
    Serial.println(address);

    address.toUpperCase();

    name = "BLESense-";
    name += address[address.length() - 5];
    name += address[address.length() - 4];
    name += address[address.length() - 2];
    name += address[address.length() - 1];

    Serial.print("name = ");
    Serial.println(name);

    BLE.setLocalName(name.c_str());
    BLE.setDeviceName(name.c_str());
    BLE.setAdvertisedService(service);

    // Add all the previously defined Characteristics
    service.addCharacteristic(sampleIdCharacteristic);
    service.addCharacteristic(temperatureCharacteristic);
    service.addCharacteristic(humidityCharacteristic);
    service.addCharacteristic(pressureCharacteristic);
    service.addCharacteristic(versionCharacteristic);
    service.addCharacteristic(accelerometerCharacteristic);
    service.addCharacteristic(gyroscopeCharacteristic);
    service.addCharacteristic(quaternionCharacteristic);
    service.addCharacteristic(bsecCharacteristic);
    service.addCharacteristic(co2Characteristic);
    service.addCharacteristic(gasCharacteristic);
    service.addCharacteristic(rgbLedCharacteristic);

    // Disconnect event handler
    BLE.setEventHandler(BLEDisconnected, blePeripheralDisconnectHandler);
    
    // Sensors event handlers
    temperatureCharacteristic.setEventHandler(BLERead, onTemperatureCharacteristicRead);
    humidityCharacteristic.setEventHandler(BLERead, onHumidityCharacteristicRead);
    pressureCharacteristic.setEventHandler(BLERead, onPressureCharacteristicRead);
    bsecCharacteristic.setEventHandler(BLERead, onBsecCharacteristicRead);
    co2Characteristic.setEventHandler(BLERead, onCo2CharacteristicRead);
    gasCharacteristic.setEventHandler(BLERead, onGasCharacteristicRead);
    rgbLedCharacteristic.setEventHandler(BLEWritten, onRgbLedCharacteristicWrite);

    versionCharacteristic.setValue(VERSION);

    BLE.addService(service);
    BLE.advertise();

    calibrate();

    // if analog input pin 0 is unconnected, random analog
    // noise will cause the call to randomSeed() to generate
    // different seed numbers each time the sketch runs.
    // randomSeed() will then shuffle the random function.
    randomSeed(analogRead(0));
  }


void calibrate() {

  Serial.println("Starting Calibration");
  BHY2.update();
  
  float ax, ay, az;
  ax = ay = az = 0.0;
  
  for (int i = 0; i < 10; i++) {
    ax += accelerometer.x();
    ay += accelerometer.y();
    az += accelerometer.z();
    delay(100);
  }

  baseline_a[0] = ax / 10.0;
  baseline_a[1] = ay / 10.0;
  baseline_a[2] = az / 10.0;

  Serial.println("STARTING ACCELERATION CALIBRATION");
  Serial.println(baseline_a[0]);
  Serial.println(baseline_a[1]);
  Serial.println(baseline_a[2]);
  Serial.println("FINISHED ACCELERATION CALIBRATION");
}

  void loop(){
    while (BLE.connected()){
      while (BLE.connected() and samplesRead == numSamples) {
        BHY2.update();
        if (accelerometerCharacteristic.subscribed()){
          float x, y, z;
          x = constrain(accelerometer.x() - baseline_a[0], -truncate, truncate) / truncate;
          y = constrain(accelerometer.y() - baseline_a[1], -truncate, truncate) / truncate;
          z = constrain(accelerometer.z() - baseline_a[2], -truncate, truncate) / truncate;

          baseline_a[0] = accelerometer.x();
          baseline_a[1] = accelerometer.y();
          baseline_a[2] = accelerometer.z();

          float aggregatedAcceleration = x + y + z;
          
          if (aggregatedAcceleration > accelerationThreshold) {
            samplesRead = 0;
            randNumber = random(100)/100.0;

            if (sampleIdCharacteristic.subscribed()){
              sampleIdCharacteristic.writeValue(randNumber);
            }

            break;
          }

        }
      }

      BHY2.update();
      
      if (gyroscopeCharacteristic.subscribed()){
        float x, y, z;

        x = constrain(gyroscope.x(), -truncate, truncate) / 25000.0;
        y = constrain(gyroscope.y(), -truncate, truncate) / 25000.0;
        z = constrain(gyroscope.z(), -truncate, truncate) / 25000.0;

        Serial.print(x);
        Serial.print(",");
        Serial.print(y);
        Serial.print(",");
        Serial.print(z);
        Serial.println("");

        float gyroscopeValues[3] = {x, y, z};

        gyroscopeCharacteristic.writeValue(gyroscopeValues, sizeof(gyroscopeValues));
      }

      if (accelerometerCharacteristic.subscribed()){
        float x, y, z;
        x = constrain(accelerometer.x() - baseline_a[0], -truncate, truncate) / truncate;
        y = constrain(accelerometer.y() - baseline_a[1], -truncate, truncate) / truncate;
        z = constrain(accelerometer.z() - baseline_a[2], -truncate, truncate) / truncate;

        baseline_a[0] = accelerometer.x();
        baseline_a[1] = accelerometer.y();
        baseline_a[2] = accelerometer.z();

        float accelerometerValues[] = {x, y, z};

        accelerometerCharacteristic.writeValue(accelerometerValues, sizeof(accelerometerValues));
      }

      if(quaternionCharacteristic.subscribed()){
        float x, y, z, w;
        x = quaternion.x();
        y = quaternion.y();
        z = quaternion.z();
        w = quaternion.w();

        float quaternionValues[] = {x,y,z,w};
        quaternionCharacteristic.writeValue(quaternionValues, sizeof(quaternionValues));
      }
      samplesRead++;
    }
  }



void blePeripheralDisconnectHandler(BLEDevice central){
    nicla::leds.setColor(red);
  }


  void onTemperatureCharacteristicRead(BLEDevice central, BLECharacteristic characteristic){
    float temperatureValue = temperature.value();
    temperatureCharacteristic.writeValue(temperatureValue);
  }


  void onHumidityCharacteristicRead(BLEDevice central, BLECharacteristic characteristic){
    uint8_t humidityValue = humidity.value();
    humidityCharacteristic.writeValue(humidityValue);
  }


  void onPressureCharacteristicRead(BLEDevice central, BLECharacteristic characteristic){
    float pressureValue = pressure.value();
    pressureCharacteristic.writeValue(pressureValue);
  }


  void onBsecCharacteristicRead(BLEDevice central, BLECharacteristic characteristic){
    float airQuality = float(bsec.iaq());
    bsecCharacteristic.writeValue(airQuality);
  }


  void onCo2CharacteristicRead(BLEDevice central, BLECharacteristic characteristic){
    uint32_t co2 = bsec.co2_eq();
    co2Characteristic.writeValue(co2);
  }


  void onGasCharacteristicRead(BLEDevice central, BLECharacteristic characteristic){
    unsigned int g = gas.value();
    gasCharacteristic.writeValue(g);
  }


  void onRgbLedCharacteristicWrite(BLEDevice central, BLECharacteristic characteristic){

    byte r = rgbLedCharacteristic[0];
    byte g = rgbLedCharacteristic[1];
    byte b = rgbLedCharacteristic[2];


    nicla::leds.setColor(r, g, b);
  }
