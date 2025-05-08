import time, datetime

alarm = None
alarm_on = False
alarm_triggered = False

def get_time():
    while True:
        current = datetime.datetime.now().replace(second=0)
        yield current.strftime("%H:%M:%S")


def run_4_segment_simulator(alarm_queue, turn_off_queue, callback, delay, stop_event, name, runsOn):
    global alarm, alarm_on, alarm_triggered
    time_generator = get_time()
    for t in time_generator:
        if alarm_queue.qsize() > 0:
            a = alarm_queue.get()
            alarm = a
        if turn_off_queue.qsize() > 0:
            alarm_on = False 
        callback(False, t)
        print(f"Current time - {t}")
        print(f"Alarm - {alarm}")
        if alarm is not None and alarm == t and not alarm_triggered:
            alarm_on = True
            alarm_triggered = True
        elif alarm is not None and alarm != t and alarm_triggered:
            alarm_triggered = False
        if alarm_on:
            callback(True, None)
            print("WAKE UP!!")
            alarm_on = False
        
        time.sleep(delay)
        if stop_event.is_set():
            break


   