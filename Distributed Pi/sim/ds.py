import time
import random


def generate_door_opened():
    while True:
        yield random.choice([True, False])

def run_ds_simulator(delay, callback, stop_event, name, runsOn):
    door_opened_generator = generate_door_opened()
    for door_opened in door_opened_generator:
        time.sleep(delay)
        callback(door_opened, name, True, runsOn)
        if stop_event.is_set():
            break