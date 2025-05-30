import RPi.GPIO as GPIO
import datetime, time

class FourSegment:
    num = {' ':(0,0,0,0,0,0,0),
    '0':(1,1,1,1,1,1,0),
    '1':(0,1,1,0,0,0,0),
    '2':(1,1,0,1,1,0,1),
    '3':(1,1,1,1,0,0,1),
    '4':(0,1,1,0,0,1,1),
    '5':(1,0,1,1,0,1,1),
    '6':(1,0,1,1,1,1,1),
    '7':(1,1,1,0,0,0,0),
    '8':(1,1,1,1,1,1,1),
    '9':(1,1,1,1,0,1,1)}

    def __init__(self, name, segments, digits):
        self.name = name
        self.segments = segments
        self.digits = digits
        self.alarm = None
        self.alarm_on = False
        for segment in self.segments:
            GPIO.setup(segment, GPIO.OUT)
            GPIO.output(segment, 0)

        for digit in digits:
            GPIO.setup(digit, GPIO.OUT)
            GPIO.output(digit, 1)        

        

def run_display_loop(alarm_queue, turn_off_queue, callback, delay, four_segment, stop_event, name, runsOn):
    try:
        while True:
            if alarm_queue.qsize() > 0:
                alarm = alarm_queue.get()
                four_segment.alarm = alarm
            if turn_off_queue.qsize() > 0:
                four_segment.alarm_on = False
            current = datetime.datetime.now().replace(second=0)
            display_time = current.strftime("%H:%M:%S")
            callback(False, display_time)
            print(display_time, four_segment.alarm)
            if display_time == four_segment.alarm:
                four_segment.alarm_on = True
                callback(True, None)
            n = time.ctime()[11:13]+time.ctime()[14:16]
            s = str(n).rjust(4)
            for digit in range(4):
                for loop in range(0, 7):
                    GPIO.output(four_segment.segments[loop], four_segment.num[s[digit]][loop])
                    if (int(time.ctime()[18:19]) % 2 == 0) and (digit == 1):
                        GPIO.output(25, 1)
                    else:
                        GPIO.output(25, 0)
                GPIO.output(four_segment.digits[digit], 0)


                if four_segment.alarm_on:
                    time.sleep(0.5)
                else:
                    time.sleep(0.001)
                GPIO.output(four_segment.digits[digit], 1)
            if stop_event.is_set():
                break
                
    finally:
        GPIO.cleanup()


