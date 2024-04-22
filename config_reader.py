import json

# def read_config(configfile):
#     with open(configfile, 'r') as config_file:
#         data = json.load(config_file)
#     return data


from RPA.Robocorp.WorkItems import WorkItems

# Initialize the Work Items library

def read_config():
    # Initialize the Work Items library
    workitems = WorkItems()

    # Load the current Work Item
    work_item = workitems.load()

    return work_item





