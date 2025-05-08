from sim.dms import run_dms_simulator
import threading, time, json
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt


sensor_data_lock = threading.Lock()
batch = []
publish_data_counter = 0
publish_data_limit = 1
counter_lock = threading.Lock()
HOSTNAME = ""
PORT = 0
pincode = ""
username="admin"
password="admin"
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(username, password)

ALARM_TRIGGERED = False
SYSTEM_ACTIVATED = False


def on_connect(client, userdata, flags, rc):
    print("DMS connected")
    client.subscribe("DMS_Data")


def on_message(client, userdata, msg):
    global ALARM_TRIGGERED, SYSTEM_ACTIVATED
    data = json.loads(msg.payload.decode('utf-8'))
    print(data)
    ALARM_TRIGGERED = data["triggered"]
    SYSTEM_ACTIVATED = data["activated"]


def publisher_task(event, _batch):
    global publish_data_counter, publish_data_limit
    while True:
        event.wait()
        with counter_lock:
            local_batch = _batch.copy()
            publish_data_counter = 0
            _batch.clear()
            publish.multiple(local_batch, hostname=HOSTNAME, port=PORT)
            print(f'published dms values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, batch,))
publisher_thread.daemon = True
publisher_thread.start()


def dms_callback(wrong_pin, name, simulated, runsOn):
    if not wrong_pin:
        global publish_data_counter, publish_data_limit, ALARM_TRIGGERED, SYSTEM_ACTIVATED
        t = time.localtime()
        t = time.strftime('%H:%M:%S', t)
        data = {
            "measurement": name,
            "name": name,
            "simulated": simulated,
            "runsOn": runsOn,
            "values": {
                "action": 1,
                "alarm_status": ALARM_TRIGGERED,
                "system_status": SYSTEM_ACTIVATED
            },
            "code": 200,
            "timestamp": t
        }
        with counter_lock:
            batch.append((name, json.dumps(data), 0, True))
            publish_data_counter += 1

        if publish_data_counter >= publish_data_limit:
            publish_event.set()
    else:
        print("Wrong pin")
        publish.single("ALERT", json.dumps({
            "measurement": "ALERT",
            "name": name,
            "runsOn": runsOn,
            "values": {
                "action": 0
            },
            "simulated": simulated,
            "code": 400,
        }), hostname=HOSTNAME, port=PORT)


def run_dms(queue, settings, threads, stop_event):
    global HOSTNAME, PORT, pincode, mqtt_client
    HOSTNAME = settings['hostname']
    PORT = settings['port']
    pincode = settings['pincode']
    mqtt_client.connect(HOSTNAME, PORT, keepalive=65535)
    mqtt_client.loop_start()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    if settings["simulated"]:
        print("Starting DMS simulator")
        dms_thread = threading.Thread(target=run_dms_simulator, args=(queue, 3, dms_callback, stop_event, settings['name'], settings['runsOn'], settings['pincode']))
        dms_thread.start()
        threads.append(dms_thread)
        print("DMS simulator started")
    else:
        from sensors.dms import run_dms_loop, DMS
        print("Starting DMS loop")
        dms = DMS(settings['name'], settings['pins'], settings['pincode'])
        dms_thread = threading.Thread(target=run_dms_loop, args=(dms, 2, dms_callback, stop_event, settings['name'], settings['runsOn']))
        dms_thread.start()
        threads.append(dms_thread)
        print("DMS loop started")