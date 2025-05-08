import time, threading, json
from queue import Queue
from sim.ir import run_ir_simulator
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
            print(f'published IR values')
        event.clear()

publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, batch,))
publisher_thread.daemon = True
publisher_thread.start()


def callback(button_pressed):
    global sensor_data_lock, publish_data_counter, publish_data_limit
    data = {
        "button_pressed": button_pressed
    }
    with counter_lock:
        batch.append(("IR", json.dumps(data), 0, True))
        publish_data_counter += 1
    if publish_data_counter >= publish_data_limit:
        publish_event.set()



def run_ir(settings, threads, stop_event, input_queue):
    global HOSTNAME, PORT, mqtt_client
    HOSTNAME = settings['hostname']
    PORT = settings['port']
    mqtt_client.connect(HOSTNAME, PORT, keepalive=65535)
    mqtt_client.loop_start()
    if settings['simulated']:
        print("Starting IR simulator") 
        ir_thread = threading.Thread(target=run_ir_simulator, args=(input_queue, 0.2, callback, stop_event, settings['name'], settings['runsOn']))
        ir_thread.start()
        threads.append(ir_thread)
        print("IR simulator started")
    else:
        from sensors.ir import run_ir_loop, IR
        print("Starting IR loop")
        ir = IR(settings['name'], settings['pin'])
        ir_thread = threading.Thread(target=run_ir_loop, args=(callback, ir, 0.2, stop_event, settings['name'], settings['runsOn']))
        ir_thread.start()
        threads.append(ir_thread)
        print("IR loop started")