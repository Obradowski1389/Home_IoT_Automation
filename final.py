import os
import glob
import time
import RPi.GPIO as GPIO
import requests
import time
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import json

PIN1 = 17
PIN2 = 27
PIN3 = 22

SWITCH_23 = False
SWITCH_24 = False

rezim_rada=1

IDEALNA_TEMP = 22.0
aktivni_rezim = 1  # 1 - ručni, 2 - automatski, 3-PID regulacija
zadana_brzina = 1  # za ručni režim
fen_brzina = 0     # trenutno stanje ventilatora
fen_brzina_procenti=0

API_KEY="f1d9b354740060010f5db140764f3c0a"
#CITY="Novi Sad"
LAT=45.2671
LON=19.8335

URL = f"http://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
# PID kontrola
Kp = 6.0
Ki = 0.15
Kd = 2.0

integral = 0
prethodna_greska = 0.0
integral=0.0

TEMP_OFFSET=10
min_brzina = 0
max_brzina = 100
startna_temperatura=-1
isOn = True

def onConnect(client, userdata, flags, rc):
    print("connected on mqtt")
    
def onMessage(client, userdata, msg):
    global zadana_brzina, fen_brzina, IDEALNA_TEMP, rezim_rada, startna_temperatura
    global Kp, Ki, Kd, isOn
    data = json.loads(msg.payload.decode('utf-8'))
    print(data)
    if msg.topic == "change_fan":
        fen_brzina = data["fanSpeed"]
        rezim_rada=2
        zadana_brzina = fen_brzina
        print("zadana brzinaaaaaa:")
        print(zadana_brzina)
    elif msg.topic == "change_temp":
        IDEALNA_TEMP = data["temp"]
        #-----------------------------------------
        device_file = setup_sensor()
        startna_temperatura = read_temperature(device_file)
        print("gore sam, startna temp: ",startna_temperatura)
        #-----------------------------------------
        rezim_rada = data["mode"]#1:auto mode, 2: rucni mode, 3:economy
        print(rezim_rada)
        print(IDEALNA_TEMP)
    elif msg.topic == "change_pid":
        print("PIDUPDATEEEEE")
        Kp=data["p"]
        Ki=data["i"]
        Kd=data["d"]
    elif msg.topic == "change_system_state":
        isOn = data["state"]
        

def sendPersonInside(isPersonInside):
    print("sent change person")
    publish.single("person", json.dumps({"change": isPersonInside}), hostname="192.168.1.100", port=1883)
    
def sendWindowsState(isWindowOpen):
    publish.single("windows", json.dumps({"window": isWindowOpen}), hostname="192.168.1.100", port=1883)
    
username="admin"
password="admin"
mqtt_client=mqtt.Client()
mqtt_client.username_pw_set(username, password)
mqtt_client.connect("192.168.1.100", 1883, keepalive=65535)
mqtt_client.subscribe("change_fan")
mqtt_client.subscribe("change_temp")
mqtt_client.subscribe("change_pid")
mqtt_client.subscribe("change_system_state")
mqtt_client.loop_start()
mqtt_client.on_connect = onConnect
mqtt_client.on_message = onMessage



'''
    Senzor temperature
    Koriscenje: 
        1) pozvati sensor = setup_sensor()
        2) pozvati temperatura = read_temperature(sensor)
'''
def setup_sensor():
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')

    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]  
    device_file = device_folder + '/w1_slave'
    
    return device_file

def read_temp_raw(device_file):
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_temperature(device_file):
    lines = read_temp_raw(device_file)
    
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(device_file)
    
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
    return None




'''
    LED
    Ukljuci LED: turn_on_led(LED_koji_se_ukljucuje)
    Ugasi LED: turn_off_led(LED_koji_se_gasi)
    LED1 je na Pinu 17 ukoliko je dobro povezano
    LED2 je na Pinu 27 ukoliko je dobro povezano 
    LED3 je na Pinu 22 ukoliko je dobro povezano plava zica
    
    Pinovi u programu se razlikuju po oznaci od onih na raspberry plocici
'''
def turn_on_led(pin):
    GPIO.output(pin, GPIO.HIGH)

def turn_off_led(pin):
    GPIO.output(pin, GPIO.LOW)







'''
    Prekidaci
    Procitaj stanje prekidaca: stajne_prekidaca = read_switch_state(prekidac)
    Prekidac1 je na pinu 23 ukoliko je dobro povezano
    Prekidac2 je na pinu 24 ukoliko je dobro povezano
    
    Pinovi u programu se razlikuju po oznaci od onih na raspberry plocici
'''
def read_switch_state(pin):
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    return GPIO.input(pin) == GPIO.HIGH


'''
    Rezimi rada

'''
def turn_off_all_leds():
    turn_off_led(PIN1)
    turn_off_led(PIN2)
    turn_off_led(PIN3)
def turn_on_all_leds():
    turn_on_led(PIN1)
    turn_on_led(PIN2)
    turn_on_led(PIN3)

def rucni_rezim():
    global fen_brzina
    print(f"[Ručni režim] Zadana brzina: {zadana_brzina}")

    fen_brzina = zadana_brzina
    turn_off_all_leds()

    rezim_dioda_na_osnovu_fena(fen_brzina)
        
def rezim_dioda_na_osnovu_fena(fen_brzina):
    if fen_brzina==1:
        turn_on_led(PIN1)
        turn_off_led(PIN2)
        turn_off_led(PIN3)
        
    elif fen_brzina==2:
        turn_on_led(PIN1)
        turn_on_led(PIN2)
        turn_off_led(PIN3)
    elif fen_brzina==3:
        turn_on_all_leds()
    elif fen_brzina==0:
        turn_off_all_leds()
def ugasi_sistem():
    isOn=False
    fen_brzina=0
    turn_off_all_leds()
    publish.single("system_state", json.dumps({"state": 0}), hostname="192.168.1.100", port=1883)
    
def odredjivanje_brzine_fena(temperatura):
    global fen_brzina
    odstupanje = abs(temperatura - IDEALNA_TEMP)
    if odstupanje <=1:
        fen_brzina=0
    elif 1 < odstupanje <= 2:
        fen_brzina = 1
     
    elif 2 < odstupanje <= 5:
        fen_brzina = 2
        
    else:
        fen_brzina = 3
    print(f"[Automatski režim] Odstupanje {odstupanje:.2f}°C - Fen brzina: {fen_brzina}")
    return fen_brzina
    
def odredjivanje_brzine_fena_stednja_energije(temperatura):
    global fen_brzina
    odstupanje = abs(temperatura - IDEALNA_TEMP)
    if odstupanje<=1:
        fen_brzina=0
    elif 1<odstupanje <= 4:
        fen_brzina = 1
    elif 4 < odstupanje <= 8:
        fen_brzina = 2
    else:
        fen_brzina = 3
    return fen_brzina
    

def automatski_rezim(temperatura):
    fen_brzina=odredjivanje_brzine_fena(temperatura)
    print("brzina fena: ",fen_brzina)
    rezim_dioda_na_osnovu_fena(fen_brzina)
def automatski_rezim_stednja(temperatura):
    fen_brzina=odredjivanje_brzine_fena_stednja_energije(temperatura)
    print("brzina fena: ",fen_brzina)
    rezim_dioda_na_osnovu_fena(fen_brzina)
def odredjivanje_rezima_rada(rezim_rada,temperatura):
    if(rezim_rada==1):
        print("automatski rezim")
        automatski_rezim(temperatura)
        
    elif(rezim_rada==3):
        #pid_automatski()
        automatski_pid_rezim(temperatura)
        print("pid auto")
        time.sleep(1.0)


      

        
 
def pid_regulacija(trenutna_temp, zadana_temp):
    dt=1.0
    global integral, prethodna_greska, Kp, Ki, Kd
    integral=0
    greska = abs(zadana_temp - trenutna_temp)
    
    integral=integral+greska*dt
    print("caos")
    print("integral ",integral)
    # Derivacija
    derivacija = (greska - prethodna_greska)/dt
    prethodna_greska=greska

    
    izlaz = Kp*greska+Ki*integral+Kd*derivacija

    # Saturacija izlaza
    izlaz = max(min(izlaz, max_brzina), min_brzina)

    return izlaz
    
def automatski_pid_rezim(temperatura):
    global fen_brzina
    global fen_brzina_procenti
    print("temperaturaa ", temperatura)
    print("temperaturaa ", IDEALNA_TEMP)
    fen_brzina_procenti = pid_regulacija(temperatura, IDEALNA_TEMP)
    print(fen_brzina)
    turn_off_all_leds()  # prvo ugasimo sve diode

    # Logika paljenja dioda na osnovu procenta brzine
    if fen_brzina_procenti >= 90:
        fen_brzina=3
        
    elif fen_brzina_procenti >= 60:
        fen_brzina=2
        
    elif fen_brzina_procenti >= 7:
        fen_brzina=1
        
    elif fen_brzina_procenti < 7:
        fen_brzina=0
        
    rezim_dioda_na_osnovu_fena(fen_brzina)
    

    print(f"[Automatski PID režim] Izračunata brzina: {fen_brzina_procenti:.2f}%")
    publish.single("pid_procenat", json.dumps({"procenat": fen_brzina_procenti}), hostname="192.168.1.100", port=1883)
    
    
    
    
    
    
#----------------------------------------------------------
def get_weather_data():
    try:
        # Pošaljite GET zahtev za vremensku prognozu
        response = requests.get(URL)
        # Proveri da li je zahtev uspešan (status kod 200)
        if response.status_code == 200:
            data = response.json()  # Očitaj JSON odgovor
            temperature = data['main']['temp']  # Trenutna temperatura u °C
            description = data['weather'][0]['description']  # Opis vremena (sunčano, oblačno, itd.)

            print(f"Trenutna temperatura: {temperature}°C")
            print(f"Vreme: {description}")
            print("sent api temp")
            publish.single("api_temp", json.dumps({"temp": temperature}), hostname="192.168.1.100", port=1883)
        else:
            print(f"Greška pri povlačenju podataka. Status kod: {response.status_code}")
    except Exception as e:
        print(f"Greška: {e}")



# Beskonačna petlja za periodično dobijanje podataka


    
if __name__ == "__main__":
    #def main: mod(rucni,automatski,pi
    GPIO.setmode(GPIO.BCM)
    
    # LED diode - izlazi
    GPIO.setup(PIN1, GPIO.OUT)
    GPIO.setup(PIN2, GPIO.OUT)
    GPIO.setup(PIN3, GPIO.OUT)
    
    device_file = setup_sensor()
    temperatura=22#read_temperature(device_file)
    

    # Prekidači - ulazi
    #GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("test")

    device_file = setup_sensor()
    
    
    prevPersonInside = False
    prevWindowsState = False
    sendPersonInside(False)
    sendWindowsState(False)
    
    try:
        
        while True:
            if(isOn):
                #if(isOn==false)ugasi_sistem()
                publish.single("pid_data", json.dumps({"ki": Ki, "kp": Kp, "kd": Kd}), hostname="192.168.1.100", port=1883)
                #print("vremence")
                get_weather_data()
                #print("vremence")
                temperatura = read_temperature(device_file)
                #-------------------------------------------------------
                print("IDEALNA TEMPERATURA: ", IDEALNA_TEMP) 
                print("startna temperatura: ", startna_temperatura)
                if(startna_temperatura!=-1):
                    if(IDEALNA_TEMP<startna_temperatura):#temperatura treba da opada
                        if(temperatura>startna_temperatura+3):#temperatura raste ispisi error
                            print("evo")
                            publish.single("alarm", json.dumps({"state": 1}), hostname="192.168.1.100", port=1883)
                    else: #temperatura treba da raste
                        print("wow")
                        if(temperatura<startna_temperatura-3):#temperatura opada ispisi error
                            publish.single("alarm", json.dumps({"state": 1}), hostname="192.168.1.100", port=1883)
                #---------------------------------------------------------------
                if(temperatura>35):#ako je temperatura veca od maskimalne, alarm se pali(ako je temperatura u domu 35 stepeni treba da se alarmira, verovato je pozar npr)
                    #print("alarm")
                    publish.single("alarm", json.dumps({"state": 1}), hostname="192.168.1.100", port=1883)
                #----------------------------------------------------------------------------
                isPersonInside = read_switch_state(23)
                if prevPersonInside != isPersonInside:
                    sendPersonInside(isPersonInside)
                    prevPersonInside=isPersonInside
                isWindowOpen = read_switch_state(24)
                if prevWindowsState!= isWindowOpen:
                    sendWindowsState(isWindowOpen)
                    prevWindowsState=isWindowOpen
                    
                print("Trenutna temperatura:", temperatura)

                publish.single("api_temp_inside", json.dumps({"temp": temperatura}), hostname="192.168.1.100", port=1883)
                if (rezim_rada==2):
                    
                    publish.single("system_state", json.dumps({"state": 1}), hostname="192.168.1.100", port=1883)
                    rucni_rezim()
                else:
                    if (isWindowOpen):#otvoren je prozor
                        print(1)
                        ugasi_sistem()
                        
                    else:#prozor je zatvoren
                        publish.single("system_state", json.dumps({"state": 1}), hostname="192.168.1.100", port=1883)
                        if(isPersonInside): 
                            print(2)#covek je prisutan
                            odredjivanje_rezima_rada(rezim_rada,temperatura)
                        else:
                            print("stednja")
                            automatski_rezim_stednja(temperatura)
                            
                   
                
                time.sleep(2)
                publish.single("type_state", json.dumps({"state": rezim_rada}), hostname="192.168.1.100", port=1883)
                publish.single("fanspeed_display", json.dumps({"speed": fen_brzina}), hostname="192.168.1.100", port=1883)
                print("Idealna: ",IDEALNA_TEMP)
            else:
                time.sleep(1)

    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Program prekinut!")

    finally:
        GPIO.cleanup()
