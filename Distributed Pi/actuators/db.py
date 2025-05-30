import RPi.GPIO as GPIO
import time
from queue import Queue

cL = 129
cLS = 139
dL = 146
dLS = 156
eL = 163
fL = 173
fLS = 185
gL = 194
gLS = 207
aL = 219
aLS = 228
bL = 232

c = 261
cS = 277
d = 294
dS = 311
e = 329
f = 349
fS = 370
g = 391
gS = 415
a = 440
aS = 455
b = 466

cH = 523
cHS = 554
dH = 587
dHS = 622
eH = 659
fH = 698
fHS = 740
gH = 784
gHS = 830
aH = 880
aHS = 910
bH = 933

class DoorBuzzer:
    def __init__(self, name, pin):
        self.name = name
        self.pin = pin
        self.interrupt = Queue()
        GPIO.setup(self.pin, GPIO.OUT)

    def turn_on(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def turn_off(self):
        GPIO.output(self.pin, GPIO.LOW)

    def is_buzzer_on(self):
        return GPIO.input(self.pin) == GPIO.HIGH
    
    def buzz(self, note, duration):
        beep_delay = 1.0 / note
        time_on = beep_delay * 1_000_000 / 2
        time_off = time_on

        # Calculate the number of cycles to achieve the desired duration
        cycles = int((duration * 1_000) / (time_on + time_off))

        for _ in range(cycles):
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(time_on / 1_000_000)

            GPIO.output(self.pin, GPIO.LOW)
            time.sleep(time_off / 1_000_000)

            if self.interrupt.qsize() > 0 and self.interrupt.get():
                break

        # Add a little delay to separate the single notes
        GPIO.output(self.pin, GPIO.LOW)
        time.sleep(0.02)


    def play(self):
        notes = [a, a, f, cH,   
                a, f, cH, a, eH,    
                eH, eH, fH, cH, gS, 
                f, cH, a, aH, a,
                a, aH, gHS, gH, fHS,
                fH, fHS]
        duration = [500, 500, 350, 150,
                     500, 350, 150, 1000, 500,
                    500, 500, 350, 150, 500,
                    350, 150, 1000, 500, 350,
                    150, 500, 250, 250, 125,
                    125, 250]
        
        t=0
        for n in notes:
            if self.interrupt.qsize() > 0 and self.interrupt.get():
                self.turn_off()
                return
            self.buzz(n, duration[t])
            t+=1
        time.sleep(0.25)
        
    
def run_db_loop(should_turn_on_db, should_turn_on_bb, input_queue, db, delay, callback, stop_event, name, runsOn):
    alarm_on = False
    wake_up = False
    should_turn_on = Queue()
    if name == "DB":
        print("Starting DB loop")
        should_turn_on = should_turn_on_db
    elif name == "BB":
        print("Starting BB loop")
        should_turn_on = should_turn_on_bb
    while True:
        if should_turn_on.qsize() > 0:
            alarm_on = should_turn_on.get()
            if alarm_on:
                db.turn_on()
                callback(True, name, False, runsOn)
            else:

                db.turn_off()
                callback(False, name, False, runsOn)
        if input_queue.qsize() > 0 and name == "BB":
            wake_up = input_queue.get()
            if wake_up:
                db.play()
                callback(True, name, False, runsOn)
            else:
                db.interrupt.put(True)
                db.turn_off()
                callback(False, name, False, runsOn)
        if stop_event.is_set():
            break
        if alarm_on:
            alarm_on = False
            time.sleep(10)
            print("Buzzer ", name, " OFF")
            db.turn_off()
            callback(False, name, False, runsOn)
        else:
            time.sleep(0.2)