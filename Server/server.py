from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, join_room
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import paho.mqtt.client as mqtt
import json, time, threading
import paho.mqtt.publish as publish
import datetime


socketio = None
mqtt_client = None
influxdb_client = None
org = ""
url = ""
bucket = ""

ALARM_TRIGGERED = False
SYSTEM_ACTIVATED = True

g_temp = []
g_humidity = []
dht_treshold = 10

dpir1_motion_data = []
dpir1_treshold_percentage = 50
dpir1_motion_data_len_treshold = 10

ds_readings = []
ds_readings_len_treshold = 10
ds_threshold_percentage = 50

people_count = 0
api_temp=20
windows=0
api_temp_inide=20
system_state=1
kp=0
ki=0
kd=0
procenat=0
type_state=0
fen_brzina=0

def send_ws_message(topic, message):
    print("Sending web socket message: ", message, topic)
    socketio.emit(topic, message)


def send_message(topic, message):
    print("Sending message: ", message, topic)
    publish.single(topic, message, hostname="192.168.1.100", port=1883)

def send_alarm():
    global ALARM_TRIGGERED
    send_message("ALARM", json.dumps({"alarm": 1 if ALARM_TRIGGERED else 0}))
    time.sleep(10)


activation_thread = threading.Thread(target=send_alarm)
activation_thread.start()


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("person")
    client.subscribe("api_temp")
    client.subscribe("windows")
    client.subscribe("api_temp_inside")
    client.subscribe("system_state")
    client.subscribe("pid_data")
    client.subscribe("pid_procenat")
    client.subscribe("type_state")
    client.subscribe("fanspeed_display")
    client.subscribe("alarm")

    client.subscribe("RDHT1")
    client.subscribe("RDHT2")
    client.subscribe("RDHT3")
    client.subscribe("RDHT4")
    client.subscribe("GDHT")

    client.subscribe("RPIR1")
    client.subscribe("RPIR2")
    client.subscribe("RPIR3")
    client.subscribe("RPIR4")
    client.subscribe("DPIR1")
    client.subscribe("DPIR2")
    
    client.subscribe("DUS1")
    client.subscribe("DUS2")

    client.subscribe("DS1")
    client.subscribe("DS2")
    client.subscribe("DL")
    client.subscribe("DB")
    client.subscribe("BB")
    client.subscribe("DMS")
    #send_message("DMS_Data", json.dumps({"triggered": ALARM_TRIGGERED, "activated": SYSTEM_ACTIVATED}))

    client.subscribe("GSG")
    client.subscribe("ALERT")
    client.subscribe("B4SD")
    client.subscribe("IR")


def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode('utf-8'))
    topic = msg.topic
    print(topic)
    parse_data(data, topic)


def parse_data(data, topic=None):
    global ALARM_TRIGGERED, SYSTEM_ACTIVATED


    if topic == "ALERT" and SYSTEM_ACTIVATED:
        trigger_alarm(data['name'], data["runsOn"], data["simulated"])
        ALARM_TRIGGERED = True

    elif SYSTEM_ACTIVATED:
        if topic == "GDHT":
            msg = parse_gdht(data)
            if msg:
                send_message("GDHT_Data", msg)
            write_to_db(data)
        elif topic == "person":
            global people_count
            if data['change']:
                people_count = 1
            else:
                people_count = 0
            send_ws_message("people_count", json.dumps({"people_count": people_count}))
            write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
            point = (
                Point("people_count")
                .tag("name", "change")
                .tag("simulated", False)
                .tag('runsOn', "pi2")
                .tag('code', "200")
            )

            point.field("peopleCount", float(people_count))
            timestamp_str = datetime.datetime.now().isoformat()
            point.field("timestamp", timestamp_str)

            write_api.write(bucket=bucket, org=org, record=point)
        elif topic == "windows":
            global windows
            if data['window']:
                windows = 1
            else:
                windows = 0
            send_ws_message("windows", json.dumps({"window": windows}))
            write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
            point = (
                Point("windows")
                .tag("name", "change")
                .tag("simulated", False)
                .tag('runsOn', "pi2")
                .tag('code', "200")
            )

            point.field("window", float(windows))
            timestamp_str = datetime.datetime.now().isoformat()
            point.field("timestamp", timestamp_str)

            write_api.write(bucket=bucket, org=org, record=point)
        elif topic == "system_state":
            global system_state
            if data['state']:
                system_state = 1
            else:
                system_state = 0
            send_ws_message("system_state", json.dumps({"state": system_state}))
            write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
            point = (
                Point("system_state")
                .tag("name", "change")
                .tag("simulated", False)
                .tag('runsOn', "pi2")
                .tag('code', "200")
            )

            point.field("state", float(system_state))
            timestamp_str = datetime.datetime.now().isoformat()
            point.field("timestamp", timestamp_str)

            write_api.write(bucket=bucket, org=org, record=point)
        elif topic == "api_temp":
            global api_temp
            api_temp = data['temp']
            send_ws_message("api_temp", json.dumps({"temp": api_temp}))
            write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
            point = (
                Point("API_TEMP")
                .tag("name", "temp")
                .tag("simulated", False)
                .tag('runsOn', "pi2")
                .tag('code', "200")
            )
            point.field("API_TEMP", float(api_temp))
            timestamp_str = datetime.datetime.now().isoformat()
            point.field("timestamp", timestamp_str)
            write_api.write(bucket=bucket, org=org, record=point)
        elif topic == "api_temp_inside":
            global api_temp_inide
            api_temp_inide = data['temp']
            send_ws_message("api_temp_inside", json.dumps({"temp": api_temp_inide}))
            write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
            point = (
                Point("API_TEMP_inside")
                .tag("name", "temp")
                .tag("simulated", False)
                .tag('runsOn', "pi2")
                .tag('code', "200")
            )
            point.field("API_TEMP_INSIDE", float(api_temp_inide))
            timestamp_str = datetime.datetime.now().isoformat()
            point.field("timestamp", timestamp_str)
            write_api.write(bucket=bucket, org=org, record=point)
        elif topic == "pid_data":
            global kp, ki, kd
            kp = data['kp']
            ki = data['ki']
            kd = data['kd']
            send_ws_message("pid_data", json.dumps({"kp": kp, "ki": ki, "kd": kd}))
            write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
            point = (
                Point("pid_data")
                .tag("name", "pid")
                .tag("simulated", False)
                .tag('runsOn', "pi2")
                .tag('code', "200")
            )
            point.field("kp", float(kp))
            point.field("ki", float(ki))
            point.field("kd", float(kd))
            
            timestamp_str = datetime.datetime.now().isoformat()
            point.field("timestamp", timestamp_str)
            write_api.write(bucket=bucket, org=org, record=point)
        elif topic == "pid_procenat":
            global procenat
            procenat = data["procenat"]
            send_ws_message("pid_procenat", json.dumps({"procenat": procenat}))
            write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
            point = (
                Point("pid_procenat")
                .tag("name", "pid_procenat")
                .tag("simulated", False)
                .tag('runsOn', "pi2")
                .tag('code', "200")
            )
            point.field("procenat", float(procenat))
            
            timestamp_str = datetime.datetime.now().isoformat()
            point.field("timestamp", timestamp_str)
            write_api.write(bucket=bucket, org=org, record=point)
        elif topic == "type_state":
            global type_state
            type_state = data["state"]
            send_ws_message("type_state", json.dumps({"type_state": type_state}))
            write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
            point = (
                Point("type_state")
                .tag("name", "type_state")
                .tag("simulated", False)
                .tag('runsOn', "pi2")
                .tag('code', "200")
            )
            point.field("type_state", float(type_state))
            
            timestamp_str = datetime.datetime.now().isoformat()
            point.field("timestamp", timestamp_str)
            write_api.write(bucket=bucket, org=org, record=point)
        elif topic == "fanspeed_display":
            global fen_brzina
            fen_brzina = data["speed"]
            send_ws_message("fanspeed_display", json.dumps({"speed": fen_brzina}))
            write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
            point = (
                Point("fen_brzina")
                .tag("name", "fen_brzina")
                .tag("simulated", False)
                .tag('runsOn', "pi2")
                .tag('code', "200")
            )
            point.field("fen_brzina", float(fen_brzina))
            
            timestamp_str = datetime.datetime.now().isoformat()
            point.field("timestamp", timestamp_str)
            write_api.write(bucket=bucket, org=org, record=point)
        
        elif topic == "alarm":
            write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
            point = (
                Point("alarm")
                .tag("name", "alarm")
                .tag("simulated", False)
                .tag('runsOn', "pi2")
                .tag('code', "200")
            )
            point.field("alarm", float(1))
            
            timestamp_str = datetime.datetime.now().isoformat()
            point.field("timestamp", timestamp_str)
            write_api.write(bucket=bucket, org=org, record=point)
            send_ws_message("ALARM", json.dumps({"alarm": 1, "activated": SYSTEM_ACTIVATED}))
            send_message("ALARM", json.dumps({"alarm": 1}))
        elif topic == "DPIR1":
            parse_pir_(data)
            if parse_pir(data):
                send_message("DL_Data", json.dumps({"motion_detected": 1}))
            write_to_db(data)
        elif topic == "DPIR2" or topic.startswith("RPIR"):
            parse_pir_(data)
            write_to_db(data)
        elif topic == "DS1" or topic == "DS2":
            if parse_ds(data):
                if not ALARM_TRIGGERED:
                    trigger_alarm(topic, data["runsOn"], data["simulated"])
                    ALARM_TRIGGERED = True
            else:
                ALARM_TRIGGERED = False
        elif topic == "DMS":
            parse_dms(data)
        elif topic == "B4SD":
            parse_b4sd(data)
        elif topic == "IR":
            parse_ir(data)
        elif topic == "DUS1" or topic == "DUS2":
            parse_dus(data)
        else:
            write_to_db(data)
    elif topic == "DMS":
        parse_dms(data)


def parse_dus(data):
    global people_count
    if isinstance(data, str):
        data = json.loads(data)
    change = data.get('change', 0)
    if change == -1 and people_count == 0:
        print("No people to exit")
        return
    people_count += change
    send_ws_message("people_count", json.dumps({"people_count": people_count}))

def parse_ir(data):
    # print(data)
    if isinstance(data, str):
        data = json.loads(data)
    button_pressed = data.get('button_pressed', "")
    send_message("rgb_data", json.dumps({"button_pressed": button_pressed}))
    send_ws_message("rgb_value", json.dumps({"button_pressed": button_pressed}))


def parse_b4sd(data):
    if isinstance(data, str):
        data = json.loads(data)
    alarm = data.get('alarm', 0)
    if alarm == 1:
        send_message("wake_up", json.dumps({"alarm": 1}))
        send_ws_message("wake_up", json.dumps(data))

def parse_dms(data):
    global ALARM_TRIGGERED, SYSTEM_ACTIVATED
    try:
        if isinstance(data, str):
            data = json.loads(data)
        values = data.get('values', {})
        action = values.get('action', 0)
        print(action, ALARM_TRIGGERED, SYSTEM_ACTIVATED)
        if action == 1:
            # print(ALARM_TRIGGERED, SYSTEM_ACTIVATED)
            if SYSTEM_ACTIVATED:
                if ALARM_TRIGGERED:
                    print("Turn off Alarm")
                    ALARM_TRIGGERED = False
                    send_ws_message("ALARM", json.dumps({"alarm": 0}))
                    untrigger_alarm(data['name'])
                    send_message("ALARM", json.dumps({"alarm": 0}))
                else:
                    print("Turn off system")
                    SYSTEM_ACTIVATED = False
            else:
                print("Turn on system")
                SYSTEM_ACTIVATED = True
            send_message("DMS_Data", json.dumps({"triggered": ALARM_TRIGGERED, "activated": SYSTEM_ACTIVATED}))
        else:
            if SYSTEM_ACTIVATED:
                print("Wrong pin")
                trigger_alarm(data['name'], data["runsOn"], data["simulated"])
                
                send_message("DMS_Data", json.dumps({"triggered": ALARM_TRIGGERED, "activated": SYSTEM_ACTIVATED}))
        # write_to_db(data)
    except:
        print(data)
        print("Error decoding JSON data")


def parse_ds(data):
    global ds_readings, ds_readings_len_treshold
    try:
        if isinstance(data, str):
            data = json.loads(data)
        values = data.get('values', {})
        door_opened = values.get('door_opened', 0)
        ds_readings.append(door_opened)
    except:
        print("Error decoding JSON data")
    # print(ds_readings)
    if len(ds_readings) >= ds_readings_len_treshold:
        truthy_count = ds_readings.count(1)
        total_count = len(ds_readings)
        percentage_truthy = (truthy_count / total_count) * 100
        ds_readings = []
        return percentage_truthy >= ds_threshold_percentage


def parse_pir_(data):
    global people_count
    try:
        if isinstance(data, str):
            data = json.loads(data)
        values = data.get('values', {})
        motion_detected = values.get('motion_detected', 0)
        if motion_detected == 1.0:
            if data['name'][0] == "D":
                send_message("DUS_Data", json.dumps({"motion_detected": 1, "name": data['name']}))
            elif people_count == 0:
                trigger_alarm(data['name'], data["runsOn"], data["simulated"])
    except:
        print("Error decoding JSON data")

def parse_pir(data):
    global dpir1_motion_data, dpir1_treshold_percentage, dpir1_motion_data_len_treshold
    try:
        if isinstance(data, str):
            data = json.loads(data)
        values = data.get('values', {})
        motion_detected = values.get('motion_detected', 0)
        dpir1_motion_data.append(motion_detected)
    except:
        print("Error decoding JSON data")
    # print(dpir1_motion_data)
    if len(dpir1_motion_data) >= dpir1_motion_data_len_treshold:
        truthy_count = dpir1_motion_data.count(1)
        total_count = len(dpir1_motion_data)
        percentage_truthy = (truthy_count / total_count) * 100
        dpir1_motion_data = []
        return percentage_truthy >= dpir1_treshold_percentage
    

def parse_gdht(data):
    global g_temp, g_humidity, dht_treshold
    try:
        if isinstance(data, str):
            data = json.loads(data)
        values = data.get('values', {})

        temperature = values.get('temperature', 0)
        humidity = values.get('humidity', 0)
        if -20 < temperature < 50 and 0 < humidity < 100:
            g_temp.append(temperature)
            g_humidity.append(humidity)
    except:
        print("Error decoding JSON data")
        return json.dumps({"temperature": 0, "humidity": 0})
    if len(g_temp) >= dht_treshold:
        average_temperature = round(sum(g_temp) / len(g_temp),1)
        average_humidity = round(sum(g_humidity) / len(g_humidity),1)
        g_temp = []
        g_humidity = []
        return json.dumps({"temperature": average_temperature, "humidity": average_humidity})


def trigger_alarm(trigger, pi, simulated):
    send_message("ALARM", json.dumps({"alarm": 1}))

    t = time.strftime('%H:%M:%S', time.localtime())
    data = {
        "measurement": "ALARM",
        "name": "ALARM",
        "trigger": trigger,
        "simulated": simulated,
        "runsOn": pi,
        "values": {
            "alarm": 1
        },
        "code": 200,
        "timestamp": t
    }
    write_alarm(data)

    send_ws_message("ALARM", json.dumps({"alarm": 1}))

def untrigger_alarm(trigger):
    t = time.strftime('%H:%M:%S', time.localtime())
    data = {
        "measurement": "ALARM",
        "name": "ALARM",
        "trigger": trigger,
        "values": {
            "alarm": 0
        },
        "code": 200,
        "timestamp": t
    }
    write_alarm(data)


def write_alarm(data):
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    point = (
        Point(data["measurement"])
        .tag("name", data["name"])
        .tag("trigger", data["trigger"])
        .tag('code', data["code"])
    )
    for field_name, field_value in data["values"].items():
        point.field(field_name, float(field_value))
    point.field("timestamp", data["timestamp"])

    write_api.write(bucket=bucket, org=org, record=point)


def write_to_db(data):
    # print(data)
    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)
    point = (
        Point(data["measurement"])
        .tag("name", data["name"])
        .tag("simulated", data["simulated"])
        .tag('runsOn', data["runsOn"])
        .tag('code', data["code"])
    )
    for field_name, field_value in data["values"].items():
        point.field(field_name, float(field_value))
    point.field("timestamp", data["timestamp"])

    write_api.write(bucket=bucket, org=org, record=point)


def to_time(date_string): 
    try:
        return datetime.datetime.strptime(date_string, "%H:%M").time()
    except ValueError:
        raise ValueError('{} is not valid time in the format HH:mm'.format(date_string))


def create_app():
    global socketio, mqtt_client, influxdb_client, bucket, org
    app = Flask(__name__)

    # Configuration options
    app.config['DEBUG'] = False

    CORS(app)
    socketio = SocketIO(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # InfluxDB Configuration
    token = "MSDAEsjtZVSLxmOmkYf83rCFW_gLQiuCMDnVUP95qvUdxTLjAUn9Q5AZwkAAA5LD2z-uZKyDUn3oTgW32aWT0g=="
    org = "iot"
    url = "http://localhost:8086"
    bucket = "iote"
    influxdb_client = InfluxDBClient(url=url, token=token, org=org)

    mqtt_client = mqtt.Client()
    username = "admin"
    password = "admin"

    mqtt_client.username_pw_set(username, password)
    mqtt_client.connect("192.168.1.100", 1883)
    mqtt_client.enable_logger()
    mqtt_client.loop_start()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    @app.route('/')
    def hello():
        return 'Hello, World!'


    @app.route('/api/set_wakeup_time', methods=['GET'])
    def set_wakeup_time():
        try:
            time = to_time(request.args.get('time'))
            print(f"Setting wakeup time to {time}")
            send_message("wake_up_data", json.dumps({"alarm_time": str(time), "turn_off": str(False)}))
            return jsonify({}), 200
        except ValueError as ex:
            return jsonify({'error': str(ex)}), 400 
        
    @app.route('/api/turn_off_wakeup', methods=['GET'])
    def turn_off_wakeup():
        try:
            send_message("wake_up_data", json.dumps({"alarm_time": "", "turn_off": str(True)}))
            send_message("wake_up", json.dumps({"alarm": 0}))
            return jsonify({}), 200
        except ValueError as ex:
            return jsonify({'error': str(ex)}), 400
        
    @app.route("/api/change_rgb", methods=["PUT"])
    def change_rgb():
        try:
            data = request.get_json()
            color = data.get('color')
            
            if color is None:
                raise ValueError("Color parameter is missing in the request body")

            print(f"Changing rgb to {color}")
            send_message("rgb_data", json.dumps({"button_pressed": color}))
            return jsonify({}), 200
        except ValueError as ex:
            return jsonify({'error': str(ex)}), 400
        
    @app.route("/api/turn_off_alarm", methods=["GET"])
    def turn_off_alarm():
        try:
            global ALARM_TRIGGERED
            ALARM_TRIGGERED = False
            send_message("ALARM", json.dumps({"alarm": 0}))
            untrigger_alarm("web")
            return jsonify({}), 200
        except ValueError as ex:
            return jsonify({'error': str(ex)}), 400
    
    @app.route("/api/fanSpeed", methods=["PUT"])
    def changeFanSpeed():
        try:
            data = request.get_json()
            fanSpeed = data.get('fanSpeed')
            if fanSpeed is None:
                raise ValueError("Fanspeed parameter is missing in the request body")
            send_message("change_fan", json.dumps({"fanSpeed": fanSpeed}))
            return jsonify({}), 200
        except ValueError as ex:
            return jsonify({'error': str(ex)}), 400

    
    @app.route("/api/temp", methods=["PUT"])
    def changetemperature():
        print("change")
        try:
            data = request.get_json()
            temp = data.get('temp')
            mode = data.get('mode')
            if temp is None or mode is None:
                raise ValueError("Temp or Mode parameter is missing in the request body")
            print("Change temp")
            send_message("change_temp", json.dumps({"temp": temp, "mode": mode}))
            return jsonify({}), 200
        except ValueError as ex:
            return jsonify({'error': str(ex)}), 400
    
    @app.route("/api/PID", methods=["PUT"])
    def changePID():
        try:
            data = request.get_json()
            p = data.get('param1')
            i = data.get('param2')
            d = data.get('param3')
            if p is None or i is None or d is None:
                raise ValueError("Temp or Mode parameter is missing in the request body")
            print("Change pid")
            send_message("change_pid", json.dumps({"p": p, "i": i, "d": d}))
            return jsonify({}), 200
        except ValueError as ex:
            return jsonify({'error': str(ex)}), 400
    
    @app.route("/api/systemState", methods=["PUT"])
    def changeSystemState():
        try:
            data = request.get_json()
            send_message("change_system_state", json.dumps({"state": data["state"]}))
            return jsonify({}), 200
        except ValueError as ex:
            return jsonify({'error': str(ex)}), 400
    
    return app

    

if __name__ == '__main__':
    global app
    app = create_app()
    app.run()


@socketio.on('subscribe')
def handle_subscribe(topic):
    join_room(topic)
    # print(f"Subscribed to {topic}")




