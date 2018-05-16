from datetime import datetime, timedelta
from dateutil import parser

import args
import helper
import boto3


class IamGroups:

    def __init__(self, **kwargs):
        self.iam_groups = kwargs.get('iam_groups', [])
        args.arguments.logger.debug(f"iam_groups= {self.iam_groups}")

        self.aws_iam = boto3.resource('iam')
        self.errors = []

    def authorize(self):
        now = datetime.now()
        expire = now + timedelta(days=0, seconds=args.arguments.time_to_expire)

        def _(aws_group, aws_user):
            aws_user.add_group(GroupName=aws_group.name)
            expired_at = args.Arguments.EXPIRED_AT % helper.str_isotime(expire)
            aws_user.create_policy(
                PolicyName=args.Arguments.FAKE_POLICY_NAME % aws_group.name,
                PolicyDocument=args.Arguments.FAKE_POLICY_DOC % ('Allow', expired_at)
            )
            args.arguments.logger.info(f'{aws_group.name}.{aws_user.name} authorized, expired at: {expired_at}')

        self.__process_iam_groups(processor=lambda aws_group, aws_user: _(aws_group, aws_user))

    def __process_iam_groups(self, processor=None):
        if not processor:
            return

        for group in self.iam_groups:
            group_name = group['group_name']
            aws_group = self.aws_iam.Group(name=group_name)
            for user_name in group['user_names']:
                adding_caller = user_name.lower() == args.arguments.api_caller.lower()
                args.arguments.logger.debug(
                    f'Adding/removing user "{user_name}" to/from group "{group_name}": {adding_caller}'
                )
                if adding_caller:
                    aws_user = self.aws_iam.User(name=user_name)
                    error = helper.get_default(fn=lambda: processor(aws_group, aws_user), ignore_error=False)
                    if error:
                        self.errors.append({'group_name': group_name, 'user_name': user_name, 'error': str(error)})

    def revoke(self):
        self.__process_iam_groups(processor=lambda aws_group, aws_user: self.__revoke(aws_group, aws_user))

    def __revoke(self, aws_group, aws_user):
        policy_name = args.Arguments.FAKE_POLICY_NAME % aws_group.name
        aws_user_policy = self.aws_iam.UserPolicy(user_name=aws_user.name, name=policy_name)
        aws_user_policy.delete()
        aws_user.remove_group(GroupName=aws_group.name)
        args.arguments.logger.info(f'{aws_group.name}.{aws_user.name} revoked')

    def clear(self):
        now = datetime.now()
        expired_term = args.Arguments.EXPIRED_AT % ""

        def _(aws_group, aws_user):
            policy_name = args.Arguments.FAKE_POLICY_NAME % aws_group.name
            aws_user_policy = self.aws_iam.UserPolicy(user_name=aws_user.name, name=policy_name)
            aws_user_policy.load()

            policy_doc = aws_user_policy.policy_document
            expired_statements = list(filter(
                lambda st: st.get('Effect', '').lower() == 'allow' and expired_term in st.get('Resource', ''),
                policy_doc['Statement']
            ))

            for statement in expired_statements:
                st_resource = statement.get('Resource', '')
                args.arguments.logger.debug(f'Clearing {aws_user.name}.{policy_name}.Resource= {st_resource}')

                expired_time = st_resource[st_resource.find(expired_term) + len(expired_term):]
                expired_time = helper.get_default(fn=lambda: parser.parse(expired_time))
                if not expired_time:
                    continue

                args.arguments.logger.debug(f"Expired time: {expired_time}")
                if now.timestamp() >= expired_time.timestamp():
                    self.__revoke(aws_group, aws_user)

        self.__process_iam_groups(processor=lambda aws_group, aws_user: _(aws_group, aws_user))
