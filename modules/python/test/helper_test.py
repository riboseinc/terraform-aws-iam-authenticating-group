import os
import json

import args

with open(f'{os.getcwd()}/groups.json', 'r') as file:
    groups_json = file.read()

args.arguments.iam_groups = json.loads(groups_json)
args.arguments.time_to_expire = 2

with open(f'{os.getcwd()}/event.json', 'r') as file:
    args = file.read()

event = json.loads(args)
