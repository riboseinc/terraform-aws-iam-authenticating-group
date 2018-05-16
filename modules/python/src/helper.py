import json
import model
import time
import boto3
import args


def get_default(fn, default=None, ignore_error=True, **kwargs):
    value = default

    try:
        result = fn(**kwargs)
        if result:
            value = result
    except Exception as error:
        print(f"catching error: {str(error)}")
        if not ignore_error:
            value = error

    return value


# def get_catch(fn, ignore_error=False, ignore_result=True, default=None, default_if_none=False, **kwargs):
#     try:
#         result = fn(**kwargs)
#         result = None if ignore_result else result
#         return default if not result and default_if_none else result
#     except Exception as error:
#         return default if ignore_error else error


def handler(fn_handler, action, event=None):
    args.arguments.logger.info(f"Boto version: {boto3.__version__}")
    args.arguments.logger.info(f"event= {event}")
    args.arguments.logger.info(f'"{args.arguments.api_caller}" calling API "{action.lower()}"')
    args.arguments.event = event

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

    except Exception as error:
        response['statusCode'] = 500
        response['body']['success'] = False
        response['body']['error'] = {
            'message': getattr(error, 'msg', str(error)),
            'details': f'type of error {type(error).__name__}'
        }

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
