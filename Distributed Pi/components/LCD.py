#!/usr/bin/env python3

from sensors.LCD.PCF8574 import PCF8574_GPIO
from sensors.LCD.Adafruit_LCD1602 import Adafruit_CharLCD
import paho.mqtt.client as mqtt

from time import sleep, strftime
from datetime import datetime
import json

username="admin"
password="admin"
mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(username, password)

temp = 0.0
humidity = 0.0
HOSTNAME = ""
PORT = 0

def on_connect(client, userdata, flags, rc):
    print("LCD connected")
    client.subscribe("GDHT_Data")
 
def on_message(client, userdata, msg):
    global temp, humidity
    data = json.loads(msg.payload.decode('utf-8'))
    temp = data["temperature"]
    humidity = data["humidity"]

def get_time_now():     # get system time
    return datetime.now().strftime('    %H:%M:%S')
    
def run_lcd_loop(settings, threads, stop_event):
    global HOSTNAME, PORT, mqtt_client
    HOSTNAME = settings['hostname']
    PORT = settings['port']
    mqtt_client.connect(HOSTNAME, PORT, keepalive=65535)
    mqtt_client.loop_start()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    if settings['simulated']:
        while True:
            global temp, humidity
            print("Temp: ", temp, "\t", "Humidity: ", humidity)
            sleep(10)
    else:
        PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
        PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.
        try:
            mcp = PCF8574_GPIO(PCF8574_address)
        except:
            try:
                mcp = PCF8574_GPIO(PCF8574A_address)
            except:
                print ('I2C Address Error !')
                exit(1)
                
        lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4,5,6,7], GPIO=mcp)
        mcp.output(3,1)     # turn on LCD backlight
        lcd.begin(16,2)     # set number of LCD lines and columns
        while(True):       
            #lcd.clear()
            lcd.setCursor(0,0)  # set cursor position
            message = 'Temp: ' + str(temp) + '\n' + 'Humid: ' + str(humidity)
            lcd.message(message)
            # print(temp, "_", humidity)
            sleep(1)   
