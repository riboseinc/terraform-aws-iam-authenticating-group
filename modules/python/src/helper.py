import args
from botocore import exceptions
import json
import model
import time


def get_catch(fn, ignore_error=False, ignore_result=True, default=None, **kwargs):
    try:
        result = fn(**kwargs)
        return None if ignore_result else result
    except Exception as error:
        return default if ignore_error else error


def handler(fn_handler, action):
    response = {
        "statusCode": 200,
        "body": {
            "action": action,
            "success": True
        }
    }

    try:
        iam_groups = model.IamGroups(iam_groups=args.arguments.iam_groups)
        fn_handler(iam_groups)
        if iam_groups.errors:
            response['statusCode'] = 400
            response['body']['success'] = False
            response['body']['error'] = {
                'message': 'Some errors occurred when sending commands to AWS',
                'details': iam_groups.errors
            }

    except exceptions.ClientError as error:
        response['statusCode'] = 500
        response['body']['success'] = False
        response['body']['error'] = str(error)

    response['body'] = json.dumps(response['body'])
    args.arguments.logger.debug("response: %s", response)
    return response


def json_loads(json_str):
    try:
        return json.loads(json_str) if json_str else None
    except json.JSONDecodeError as e:
        print(f"json_loads error: {e}")
    return json_loads(json_str[1:-1])


def str_isotime(ddate):
    return f'{ddate.isoformat()}{time.strftime("%z")}'
