import threading
import time
from scripts.load_settings import load_settings
from components.dht11 import run_dht
from components.pir import run_pir
from components.dl import run_dl
from components.hcsr04 import run_ultrasonic
from components.ds import run_ds
from components.dms import run_dms
from components.db import run_db
from components.four_segment import run_4_segment
from components.rgb import run_rgb
from components.ir import run_ir
# from components.LCD import run_lcd_loop
# from components.MPU6050.gyro import run_gyro
from queue import Queue
import paho.mqtt.publish as publish


try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except:
    pass

light_queue = Queue()
buzzer_queue = Queue()
rgb_queue = Queue()
dms_queue = Queue()
settings = {}

def run_user_input_threads(threads, stop_event):
    input_thread = threading.Thread(target=user_input_thread, args=(stop_event,))
    input_thread.start()
    threads.append(input_thread)


def user_input_thread(stop_event):
    global light_queue
    global buzzer_queue
    global rgb_queue

    while True:
        user_input = input()
        if user_input == 'l':
            light_queue.put(user_input)
        if user_input == 'b':
            buzzer_queue.put(user_input)
        else: 
            rgb_queue.put(user_input)
            dms_queue.put(user_input)
        time.sleep(0.1)
        if stop_event.is_set():
            break


def load_sensor_setting(pi_settings):
    global settings
    for obj in pi_settings:
        settings[obj] = pi_settings[obj]


def run_all_dht(threads, stop_event):
    run_dht(settings['RDHT1'], threads, stop_event)
    run_dht(settings['RDHT2'], threads, stop_event)
    run_dht(settings['RDHT3'], threads, stop_event)
    run_dht(settings['GDHT'], threads, stop_event)
    run_dht(settings['RDHT4'], threads, stop_event)


def run_all_pir(threads, stop_event):
    run_pir(settings['RPIR1'], threads, stop_event)
    run_pir(settings['RPIR2'], threads, stop_event)
    run_pir(settings['DPIR1'], threads, stop_event)
    run_pir(settings['RPIR3'], threads, stop_event)
    run_pir(settings['DPIR2'], threads, stop_event)
    run_pir(settings['RPIR4'], threads, stop_event)


def run_all_buttons(threads, stop_event):
    # run_ds(settings['DS1'], threads, stop_event)
    # run_dms(dms_queue, settings['DMS'], threads, stop_event)
    # run_dl(light_queue, settings['DL'], threads, stop_event)
    run_db(buzzer_queue, settings['DB'], threads, stop_event)
    # run_ds(settings['DS2'], threads, stop_event)
    # run_db(buzzer_queue, settings['BB'], threads, stop_event)
           

def run_all_ultrasonic(threads, stop_event):
    run_ultrasonic(settings['DUS1'], threads, stop_event)
    run_ultrasonic(settings['DUS2'], threads, stop_event)

def run_display(threads, stop_event):
    # run_4_segment(settings["B4SD"], threads, stop_event)
    run_rgb(settings["BRGB"], threads, stop_event)
    run_ir(settings["BIR"], threads, stop_event, rgb_queue)
    # run_lcd_loop(settings['GLCD'], threads, stop_event)


def run_all_gyro(threads, stop_event):
    # run_gyro(settings['GSG'], threads, stop_event)
    pass


if __name__ == "__main__":
    print("*** G3 Tim7 ***")
    threads = []
    stop_event = threading.Event()
    pi_settings = load_settings("1")

    try:
        load_sensor_setting(pi_settings)

        run_user_input_threads(threads, stop_event)

        # run_all_dht(threads, stop_event)
        run_all_pir(threads, stop_event)
        # run_all_buttons(threads, stop_event)
        run_all_ultrasonic(threads, stop_event)
        # run_all_gyro(threads, stop_event)
        # run_display(threads, stop_event)

        while True:
            time.sleep(5)


    except KeyboardInterrupt:
        print('Stopping app')
        for t in threads:
            stop_event.set()