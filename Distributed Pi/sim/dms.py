import time
import random


def run_dms_simulator(queue, delay, callback, stop_event, name, runsOn, pincode):
    while True:
        if queue.qsize() > 0:
            input = queue.get()
            if input == pincode:
                callback(False, name, True, runsOn)
            else:
                callback(True, name, True, runsOn)
        time.sleep(delay)
        if stop_event.is_set():
            break