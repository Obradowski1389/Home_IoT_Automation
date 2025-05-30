import time, threading, json
from sim.pir import run_pir_simulator
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt


sensor_data_lock = threading.Lock()
batch = []
publish_data_counter = 0
publish_data_limit = 5
counter_lock = threading.Lock()
HOSTNAME = ""
PORT = 0
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
            print(f'published pir values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, batch,))
publisher_thread.daemon = True
publisher_thread.start()


def pir_callback(motion_detected, name, simulated, runsOn):
    global sensor_data_lock, publish_data_counter, publish_data_limit

    t = time.localtime()
    t = time.strftime('%H:%M:%S', t)
    data = {
        "measurement": name,
        "name": name,
        "simulated": simulated,
        "runsOn": runsOn,
        "values": {
            "motion_detected": 1.0 if motion_detected else 0.0
        },
        "code": 200,
        "timestamp": t
    }
    with counter_lock:
        batch.append((name, json.dumps(data), 0, True))
        publish_data_counter += 1
        if motion_detected:
            publish.single(data['name'], json.dumps(data), hostname=HOSTNAME, port=PORT)

    if publish_data_counter >= publish_data_limit:
        publish_event.set()


def run_pir(settings, threads, stop_event):
    global HOSTNAME, PORT, mqtt_client
    HOSTNAME = settings['hostname']
    PORT = settings['port']
    mqtt_client.connect(HOSTNAME, PORT, keepalive=65535)
    mqtt_client.loop_start()
    if settings['simulated']:
        print("Starting PIR simulator")
        pir_thread = threading.Thread(target=run_pir_simulator, args=(3, pir_callback, stop_event, settings['name'], settings['runsOn']))
        pir_thread.start()
        threads.append(pir_thread)
        print("PIR simulator started")
    else:
        from sensors.pir import run_pir_loop, PIR
        print("Starting PIR loop")
        pir = PIR(settings['name'], settings['pin'])
        pir_thread = threading.Thread(target=run_pir_loop, args=(pir, 2, pir_callback, stop_event, settings['name'], settings['runsOn']))
        pir_thread.start()
        threads.append(pir_thread)
        print("PIR loop started")