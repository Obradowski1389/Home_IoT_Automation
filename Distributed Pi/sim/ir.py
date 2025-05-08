import time
from queue import Queue

def run_ir_simulator(input_queue, delay, callback, stop_event, name, runsOn):
    while True:
        if input_queue.qsize() > 0:
            user_input = input_queue.get()
            callback(user_input)
        if stop_event.is_set():
            break
        time.sleep(delay)