from sim.hcsr04 import run_ultrasonic_simulator  # Import the ultrasonic simulator
from collections import deque
import threading, time, json
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

sensor_data_lock = threading.Lock()
batch = []
publish_data_counter = 0
publish_data_limit = 5
counter_lock = threading.Lock()
HOSTNAME = ""
PORT = 0
NAME = ""
username = "admin"
password = "admin"

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(username, password)

max_distance = 400
min_distance = 2
last_distances = deque(maxlen = 5)

def on_connect(client, userdata, flags, rc):
    print("DUS connected")
    client.subscribe("DUS_Data")

def on_message(client, userdata, msg):
    global NAME
    data = json.loads(msg.payload.decode('utf-8'))
    print(data)
    if data['name'][-1] == NAME[-1]:
        # pir detected motion
        change = check_distance()
        publish.single(NAME, json.dumps({"change": change}), hostname=HOSTNAME, port=PORT)
        pass


def check_distance():
    global last_distances
    if len(last_distances) == 5:
        avg = sum(last_distances) / len(last_distances)

        if last_distances[-1] - avg > 5:
            # person exiting
            return -1
        elif avg - last_distances[-1] > 5:
            # person entering
            return 1
    return 0

username = "admin"
password = "admin"
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(username, password)

def publisher_task(event, _batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_batch = _batch.copy()
            publish_data_counter = 0
            _batch.clear()
            publish.multiple(local_batch, hostname=HOSTNAME, port=PORT)
            # print(local_batch)
            print(f'published hcsr values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, batch,))
publisher_thread.daemon = True
publisher_thread.start()


def ultrasonic_callback(distance, name, simulated, runsOn):
    global sensor_data_lock, publish_data_counter, publish_data_limit

    t = time.localtime()
    t = time.strftime('%H:%M:%S', t)
    data = {
        "measurement": name,
        "name": name,
        "simulated": simulated,
        "runsOn": runsOn,
        "values": {
            "distance": distance,
        },
        "code": 200,
        "timestamp": t,
    }
    with counter_lock:
        batch.append((name, json.dumps(data), 0, True))
        publish_data_counter += 1
        if(min_distance <= distance <= max_distance):
            last_distances.append(distance)

    if publish_data_counter >= publish_data_limit:
        publish_event.set()


def run_ultrasonic(settings, threads, stop_event):
    global HOSTNAME, PORT, NAME, mqtt_client
    HOSTNAME = settings['hostname']
    PORT = settings['port']
    NAME = settings["name"]
    mqtt_client.connect(HOSTNAME, PORT, keepalive=65535)
    mqtt_client.loop_start()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    if settings['simulated']:
        print("Starting Ultrasonic simulator")
        ultrasonic_thread = threading.Thread(target=run_ultrasonic_simulator, args=(2.5, ultrasonic_callback, stop_event, settings['name'], settings['runsOn']))
        ultrasonic_thread.start()
        threads.append(ultrasonic_thread)
        print("Ultrasonic simulator started")
    else:
        from sensors.hcsr04 import run_ultrasonic_loop, UltrasonicSensor
        print("Starting Ultrasonic loop")
        ultrasonic = UltrasonicSensor(settings['echo_pin'], settings['trigger_pin'])
        ultrasonic_thread = threading.Thread(target=run_ultrasonic_loop, args=(ultrasonic, 2, ultrasonic_callback, stop_event, settings['name'], settings['runsOn']))
        ultrasonic_thread.start()
        threads.append(ultrasonic_thread)
        print("Ultrasonic loop started")
