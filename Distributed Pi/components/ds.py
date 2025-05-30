from sim.ds import run_ds_simulator
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
username="admin"
password="admin"
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
            print(f'published ds values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, batch,))
publisher_thread.daemon = True
publisher_thread.start()


def ds_callback(door_opened, name, simulated, runsOn):
    global sensor_data_lock, publish_data_counter, publish_data_limit

    t = time.localtime()
    t = time.strftime('%H:%M:%S', t)
    data = {
        "measurement": name,
        "name": name,
        "simulated": simulated,
        "runsOn": runsOn,
        "values": {
            "door_opened": 1.0 if door_opened else 0.0
        },
        "code": 200,
        "timestamp": t
    }
    with counter_lock:
        batch.append((name, json.dumps(data), 0, True))
        publish_data_counter += 1

    if publish_data_counter >= publish_data_limit:
        publish_event.set()


def run_ds(settings, threads, stop_event):
    global HOSTNAME, PORT, mqtt_client
    HOSTNAME = settings['hostname']
    PORT = settings['port']
    mqtt_client.connect(HOSTNAME, PORT, keepalive=65535)
    mqtt_client.loop_start()
    if settings["simulated"]:
        print("Starting DS simulator")
        ds_thread = threading.Thread(target=run_ds_simulator, args=(4, ds_callback, stop_event, settings['name'], settings['runsOn']))
        ds_thread.start()
        threads.append(ds_thread)
        print("DS simulator started")
    else:
        from sensors.ds import run_ds_loop, DS
        print("Starting DS loop")
        ds = DS(settings['name'], settings['pin'])
        ds_thread = threading.Thread(target=run_ds_loop, args=(ds, 2, ds_callback, stop_event, settings['name'], settings['runsOn']))
        ds_thread.start()
        threads.append(ds_thread)
        print("DS loop started")