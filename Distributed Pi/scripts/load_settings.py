import json
import os



def load_settings(pi):
    current_directory = os.getcwd()

    settings_directory = os.path.join(current_directory, 'settings')
    settings_file = "pi_settings" + pi + ".json"
    settings_path = os.path.join(settings_directory, settings_file)


    with open(settings_path, 'r', buffering=100) as file:
        return json.load(file)

