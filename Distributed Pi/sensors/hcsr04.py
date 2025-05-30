import RPi.GPIO as GPIO
import time

class UltrasonicSensor:
    def __init__(self, echo_pin, trigger_pin):
        self.echo_pin = echo_pin
        self.trigger_pin = trigger_pin

    def get_distance(self):
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        
        # Ensure the sensor settles down
        GPIO.output(self.trigger_pin, False)
        time.sleep(0.3)
        
        # Send ultrasonic signal
        GPIO.output(self.trigger_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trigger_pin, False)

        # Measure the duration of the echo signal
        start_time = time.time()
        stop_time = time.time()
        
        while GPIO.input(self.echo_pin) == 0:
            start_time = time.time()
        while GPIO.input(self.echo_pin) == 1:
            stop_time = time.time()
        
        # Calculate distance from the time difference
        time_elapsed = stop_time - start_time
        distance = (time_elapsed * 34300) / 2  # Speed of sound is 34300 cm/s
        
        return distance


def run_ultrasonic_loop(ultrasonic, delay, callback, stop_event, name, runsOn):
    while True:
        distance = ultrasonic.get_distance()
        callback(distance, name, False, runsOn)
        if stop_event.is_set():
            break
        time.sleep(delay)