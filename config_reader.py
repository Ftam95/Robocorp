import json

def read_config(configfile):
    with open(configfile, 'r') as config_file:
        data = json.load(config_file)
    return data