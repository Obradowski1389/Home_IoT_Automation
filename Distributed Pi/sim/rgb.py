import time

def run_rgb_simulator(input_queue, delay, stop_event, name, runsOn):
    while True:
        if input_queue.qsize() > 0:
            user_input = input_queue.get()
            if user_input == "OK":
                print("RGB - off")
            elif user_input == "7":
                print("RGB - white")
            elif user_input == "1":
                print("RGB - red")
            elif user_input == "2":
                print("RGB - green")
            elif user_input == "3":
                print("RGB - blue")
            elif user_input == "4":
                print("RGB - yellow")
            elif user_input == "5":
                print("RGB - purple")
            elif user_input == "6":
                print("RGB - light blue")
        if stop_event.is_set():
            break

        time.sleep(delay)