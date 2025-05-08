from queue import Queue
from sim.dl import run_dl_simulator
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
should_turn_on = Queue()
mqtt_client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    print("DL connected")
    client.subscribe("DL_Data")


def on_message(client, userdata, msg):
    global should_turn_on
    data = json.loads(msg.payload.decode('utf-8'))
    print(data)
    should_turn_on.put(data["motion_detected"] == 1)


def publisher_task(event, _batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_batch = _batch.copy()
            publish_data_counter = 0
            _batch.clear()
            publish.multiple(local_batch, hostname=HOSTNAME, port=PORT)
            print(f'published dl values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, batch,))
publisher_thread.daemon = True
publisher_thread.start()


def dl_callback(light_on, name, simulated, runsOn):
    global sensor_data_lock, publish_data_counter, publish_data_limit
    t = time.localtime()
    t = time.strftime('%H:%M:%S', t)
    data = {
        "measurement": name,
        "name": name,
        "simulated": simulated,
        "runsOn": runsOn,
        "values": {
            "light_on": 1.0 if light_on else 0.0
        },
        "code": 200,
        "timestamp": t
    }
    with counter_lock:
        batch.append((name, json.dumps(data), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()


def run_dl(user_input_queue, settings, threads, stop_event):
    global HOSTNAME, PORT, should_turn_on, mqtt_client
    HOSTNAME = settings['hostname']
    PORT = settings['port']
    mqtt_client.connect(HOSTNAME, PORT, keepalive=65535)
    mqtt_client.loop_start()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    if settings["simulated"]:
        print("Starting DL simulator")
        dl_thread = threading.Thread(target=run_dl_simulator, args=(should_turn_on, user_input_queue, 4, dl_callback, stop_event, settings['name'], settings['runsOn']))
        dl_thread.start()
        threads.append(dl_thread)
        print("DL simulator started")
    else:
        from actuators.dl import run_dl_loop, DL
        print("Starting DL loop")
        dl = DL(settings['name'], settings['pin'])
        dl_thread = threading.Thread(target=run_dl_loop, args=(should_turn_on, user_input_queue, dl, 2, dl_callback, stop_event, settings['name'], settings['runsOn']))
        dl_thread.start()
        threads.append(dl_thread)
        print("DL loop started")