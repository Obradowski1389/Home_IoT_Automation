from sim.dht11 import run_dht_simulator
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
            # print(local_batch)
            print(f'published dht values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, batch,))
publisher_thread.daemon = True
publisher_thread.start()


def dht_callback(humidity, temperature, code, name, simulated, runsOn):
    global sensor_data_lock, publish_data_counter, publish_data_limit

    t = time.localtime()
    t = time.strftime('%H:%M:%S', t)
    if temperature > -20 and temperature < 60 and humidity > 0 and humidity < 60 and code == "DHTLIB_OK":
        data = {
            "measurement": name,
            "name": name,
            "simulated": simulated,
            "runsOn": runsOn,
            "values": {
                "temperature": float(temperature),
                "humidity": float(humidity),
            },
            "code": code,
            "timestamp": t
        }
        with counter_lock:
            batch.append((name, json.dumps(data), 0, True))
            publish_data_counter += 1

        if publish_data_counter >= publish_data_limit:
            publish_event.set()


def run_dht(settings, threads, stop_event):
    global HOSTNAME, PORT, mqtt_client
    HOSTNAME = settings['hostname']
    PORT = settings['port']
    mqtt_client.connect(HOSTNAME, PORT, keepalive=65535)
    mqtt_client.loop_start()
    if settings['simulated']:
        print("Starting dht1 sumulator")
        dht1_thread = threading.Thread(target = run_dht_simulator, args=(1, dht_callback, stop_event, settings['name'], settings['runsOn']))
        dht1_thread.start()
        threads.append(dht1_thread)
        print("Dht1 sumulator started")
    else:
        from sensors.dht11 import run_dht_loop, DHT
        print("Starting dht1 loop")
        print(f"pin: {settings['pin']}")
        dht = DHT(settings['name'], settings['pin'])
        dht1_thread = threading.Thread(target=run_dht_loop, args=(dht, 2, dht_callback, stop_event, settings['runsOn']))
        dht1_thread.start()
        threads.append(dht1_thread)
        print("Dht1 loop started")
