import struct

temperature_uuid = "19b10000-2001-537e-4f6c-d104768a1214"  # 4 Byte float32
humidity_uuid = "19b10000-3001-537e-4f6c-d104768a1214"  # 1 byte Uint8


async def execute_device_heartbeat(client):
    print("Executing Device Status Update")
    temp_bytes = await client.read_gatt_char(temperature_uuid)  # print(hexlify(temp_bytes))
    [temperature] = struct.unpack('f', temp_bytes)
    print("Temperature at the Moment:" + str(temperature))

    humidity_bytes = await client.read_gatt_char(humidity_uuid)
    [humidity] = struct.unpack('I', humidity_bytes)
    print("Humidity at the Moment:" + str(humidity))


def send_device_heartbeat_request(temperature, humidity):

    pass
