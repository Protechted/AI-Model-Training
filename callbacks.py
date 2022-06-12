import struct

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