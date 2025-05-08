import RPi.GPIO as GPIO
import time

class DoorSensor:
    def __init__(self, name, pin):
        self.name = name
        self.pin = pin

    def is_door_open(self):
        GPIO.setup(self.pin, GPIO.IN)
        return GPIO.input(self.pin) == GPIO.HIGH
    
def run_ds_loop(ds, delay, callback, stop_event, name, runsOn):
    while True:
        door_opened = ds.is_door_open()
        callback(door_opened, name, False, runsOn)
        if stop_event.is_set():
            break
        time.sleep(delay)
    