#!/usr/bin/env python3
import time


def run_gyro_loop(mpu, delay, accel, gyro, callback, stop_event, runsOn):
    while True:
        accel = mpu.get_acceleration()
        gyro = mpu.get_rotation()
        callback(accel, gyro, 0, "GSG", False, runsOn)
        if stop_event.is_set():
            break
        time.sleep(delay)  # Delay between readings