
from sim.gyro import run_gyro_simulator
import threading, time, json
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
try:
    from sensors.gyro import MPU6050 
except:
    pass


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
            print(f'published gyro values')
        event.clear()


publish_event = threading.Event()
publisher_thread = threading.Thread(target=publisher_task, args=(publish_event, batch,))
publisher_thread.daemon = True
publisher_thread.start()

SIGNIFICANT_CHANGE_THRESHOLD = 50 
previous_gyro_values = [0, 0, 0]
first_callback = True


def gyro_callback(accel, gyro, code, name, simulated, runsOn):
    global sensor_data_lock, publish_data_counter, publish_data_limit, first_callback, previous_gyro_values, SIGNIFICANT_CHANGE_THRESHOLD
    t = time.strftime('%H:%M:%S', time.localtime()) 
    data = {
        "measurement": name,
        "name": name,
        "simulated": simulated,
        "runsOn": runsOn,
        "values": {
            "acceleration_0": accel[0],
            "acceleration_1": accel[1],
            "acceleration_2": accel[2],
            "gyroscope_0": gyro[0],
            "gyroscope_1": gyro[1],
            "gyroscope_2": gyro[2],
        },
        "code": code,
        "timestamp": t
    }
    print(data)
    with counter_lock:
        batch.append((name, json.dumps(data), 0, True))
        publish_data_counter += 1
        if not first_callback and any(abs(current - previous) > SIGNIFICANT_CHANGE_THRESHOLD for current, previous in zip(gyro, previous_gyro_values)):
            notify_significant_change(name, runsOn, simulated)

        previous_gyro_values = gyro.copy()
        first_callback = False
    if publish_data_counter >= publish_data_limit:
        publish_event.set()


def notify_significant_change(name, runsOn, simulated):
    publish.single("ALERT", json.dumps({
        "name": name,
        "runsOn": runsOn,
        "simulated": simulated,
    }), hostname=HOSTNAME, port=PORT)
    # print("Published Alarm because of significant change in gyro values")


def run_gyro(settings, threads, stop_event):
    global HOSTNAME, PORT, mqtt_client
    HOSTNAME = settings['hostname']
    PORT = settings['port']
    mqtt_client.connect(HOSTNAME, PORT, keepalive=65535)
    mqtt_client.loop_start()
    if settings['simulated']:
        print("Starting simulated gyro")
        gyro_thread = threading.Thread(target=run_gyro_simulator, args=(1, gyro_callback, stop_event, settings['name'], settings['runsOn'],))
        gyro_thread.start()
        threads.append(gyro_thread)
        print("Started simulated gyro")
    else:
        from sensors.gyro.gyro import run_gyro_loop
        print("Starting gyro loop")
        mpu = MPU6050.MPU6050()     #instantiate a MPU6050 class object
        accel = [0]*3               #store accelerometer data
        gyro = [0]*3                #store gyroscope data
        mpu.dmp_initialize()        #initialize MPU6050
        gyro_thread = threading.Thread(target=run_gyro_loop, args=(mpu, 10, accel, gyro, gyro_callback, stop_event, settings['runsOn']))
        gyro_thread.start()
        threads.append(gyro_thread)


