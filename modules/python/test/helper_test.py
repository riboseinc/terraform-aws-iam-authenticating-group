import os
import json

import args

with open(f'{os.getcwd()}/groups.json', 'r') as file:
    groups_json = file.read()

args.arguments.iam_groups = json.loads(groups_json)
args.arguments.time_to_expire = 20

with open(f'{os.getcwd()}/event.json', 'r') as file:
    event_json = file.read()

event = json.loads(event_json)
args.arguments.event = event
