from sim.rgb import run_rgb_simulator
import threading, time, json
from queue import Queue
from sim.four_segment import run_4_segment_simulator
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

sensor_data_lock = threading.Lock()
batch = []
publish_data_counter = 0
publish_data_limit = 1
counter_lock = threading.Lock()
HOSTNAME = ""
PORT = 0
username = "admin"
password = "admin"
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(username, password)

color = Queue()

def on_connect(client, userdata, flags, rc):
    print("RGB connected")
    client.subscribe("rgb_data")

def on_message(client, userdata, msg):
    global color
    data = json.loads(msg.payload.decode('utf-8'))
    print(data)
    color.put(data["button_pressed"])


def run_rgb(settings, threads, stop_event):
    global HOSTNAME, PORT, color, mqtt_client
    HOSTNAME = settings['hostname']
    PORT = settings['port']
    mqtt_client.connect(HOSTNAME, PORT, keepalive=65535)
    mqtt_client.loop_start()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    if settings['simulated']:
        print('Starting RGB simulator')
        rgb_thread = threading.Thread(target=run_rgb_simulator, args=(color, 5, stop_event, settings['name'], settings['runsOn']))
        rgb_thread.start()
        threads.append(rgb_thread)
        print("RGB simulator started")
    else:
        from actuators.rgb import run_rgb_loop, RGB
        print("Starting RGB loop")
        rgb = RGB(settings['name'], settings["R_pin"], settings["G_pin"], settings["B_pin"])
        rgb_thread = threading.Thread(target=run_rgb_loop, args=(color, rgb, 5, stop_event, settings['name'], settings['runsOn']))
        rgb_thread.start()
        threads.append(rgb_thread)
        print("RGB loop started")