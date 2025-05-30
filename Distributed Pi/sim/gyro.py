import time
from random import random


def run_gyro_simulator(delay, callback, stop_event, name, runsOn):
    for _ in range(50):  # Simulate 50 data points
        accel = [int(100 * (2 * random() - 1)) for _ in range(3)]  # Simulate random accelerometer data
        gyro = [int(100 * (2 * random() - 1)) for _ in range(3)]   # Simulate random gyroscope data

        time.sleep(delay)
        callback(accel, gyro, "200", name, True, runsOn)
        if stop_event.is_set():
            break