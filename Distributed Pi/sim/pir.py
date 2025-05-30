import time
import random


def generate_motion():
    while True:
        yield random.choice([True, False])


def run_pir_simulator(delay, callback, stop_event, name, runsOn):
    motion_generator = generate_motion()
    for motion_detected in motion_generator:
        time.sleep(delay)
        callback(motion_detected, name, True, runsOn)
        if stop_event.is_set():
            break
