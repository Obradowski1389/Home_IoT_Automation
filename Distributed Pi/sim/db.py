import time
from queue import Queue

buzzer_status = False


def switch_buzzer():
    global buzzer_status
    buzzer_status = not buzzer_status


def run_buzzer_simulator(should_turn_on_db, should_turn_on_bb, input_queue, delay, callback, stop_event, name, runsOn):
    global buzzer_status
    should_turn_on = Queue()
    wake_up = False
    if name == "DB":
        print("Starting DB simulator")
        should_turn_on = should_turn_on_db
    elif name == "BB":
        print("Starting BB simulator")
        should_turn_on = should_turn_on_bb
    alarm_on = False
    while True:
        if should_turn_on.qsize() > 0:
            alarm_on = should_turn_on.get()
            if alarm_on:
                print("Buzzer ", name, " ON")
                buzzer_status = True
            else:
                print("#Buzzer ", name, " OFF")
                buzzer_status = False
        if input_queue.qsize() > 0 and name == "BB":
            wake_up = input_queue.get()
            if wake_up:
                print("Buzzer ", name, " ON")
                buzzer_status = True
            else:
                print("#Buzzer ", name, " OFF")
                buzzer_status = False
        callback(buzzer_status, name, True, runsOn)

        if stop_event.is_set():
            break
        if alarm_on:
            alarm_on = False
            time.sleep(10)
            print("Buzzer ", name, " OFF")
        else:
            time.sleep(delay)
