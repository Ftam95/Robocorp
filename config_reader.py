import json

# def read_config(configfile):
#     with open(configfile, 'r') as config_file:
#         data = json.load(config_file)
#     return data


from RPA.Robocorp.WorkItems import WorkItems

def read_config(configfile):
    with open(configfile, 'r') as config_file:
        data = json.load(config_file)
    return data

# Initialize the Work Items library
workitems = WorkItems()

# Load the file
config_data = read_config("config.json")

# new Work Item
workitems.add_work_item(data=config_data)

