import RPi.GPIO as GPIO
import time

class PIR:
    def __init__(self, name, pin):
        self.pin = pin
        self.name = name

    def motionDetected(self):
        GPIO.setup(self.pin, GPIO.IN)
        return GPIO.input(self.pin)


def run_pir_loop(pir, delay, callback, stop_event, name, runsOn):
    while True:
        motion_detected = pir.motionDetected()
        callback(motion_detected, name, False, runsOn)
        if stop_event.is_set():
            break
        time.sleep(delay)
