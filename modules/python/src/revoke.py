import helper


def handler(event=None, context=None):
    return helper.handler(fn_handler=lambda iam_groups: iam_groups.revoke(), action='REVOKE', event=event)