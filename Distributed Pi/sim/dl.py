import time


light_status = False

def switch_light():
    global light_status
    light_status = not light_status
    

def run_dl_simulator(should_turn_on, user_input_queue, delay, callback, stop_event, name, runsOn):
    global light_status
    motion_detected = False
    while True:
        if should_turn_on.qsize() > 0:
            motion_detected = should_turn_on.get()
            if motion_detected:
                print("Light ON")
                light_status = True
        elif user_input_queue.qsize() > 0:
            user_input = user_input_queue.get()
            if user_input == 'l':
                switch_light()
        callback(light_status, name, True, runsOn)

        if stop_event.is_set():
            break
        if motion_detected:
            motion_detected = False
            time.sleep(10)
            print("Light OFF")
        else:
            time.sleep(delay)
