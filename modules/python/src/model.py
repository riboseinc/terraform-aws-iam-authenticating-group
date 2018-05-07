from datetime import datetime, timedelta

from dateutil import parser

import args
import helper
import boto3


class IamGroups:

    def __init__(self, **kwargs):
        self.iam_groups = kwargs.get('iam_groups', [])
        args.arguments.logger.debug(self.iam_groups)
        self.aws_iam = boto3.resource('iam')
        self.errors = []

        self.event = kwargs.get('event', args.Arguments.DEFAULT_EVENT)
        if not self.event:
            raise helper.SimpleMessageError(msg="Event is None")

        self.__event_user_name = None

        args.arguments.logger.info(f"API caller user_name: {self.event_user_name}")

    @property
    def event_user_name(self):
        if not self.__event_user_name:
            user_arn = self.event['requestContext']["identity"]["userArn"]
            if user_arn: # user_arn = "arn:aws:iam::239062223385:user/operations/ext-phuong-huynh"
                self.__event_user_name = user_arn.split("/")[-1]
        return self.__event_user_name

    # def __get_fake_policy(self, aws_group):
    #     pass

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
                if self.event_user_name and user_name.upper() != self.event_user_name.upper():
                    args.arguments.logger.debug(f"Ignore process for user {user_name} since he/she not the API caller")
                    continue

                aws_user = self.aws_iam.User(name=user_name)
                error = helper.get_catch(fn=lambda: processor(aws_group, aws_user))
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
                args.arguments.logger.debug(f"{aws_user.name}.{policy_name}.Resource= {st_resource}")
                expired_time = st_resource[st_resource.find(expired_term) + len(expired_term):]
                try:
                    expired_time = parser.parse(expired_time)
                except ValueError as ve:
                    args.arguments.logger.debug('parse expired_time error: %s', ve)
                    continue

                is_expired = now.timestamp() >= expired_time.timestamp()
                if is_expired:
                    self.__revoke(aws_group, aws_user)

        self.__process_iam_groups(processor=lambda aws_group, aws_user: _(aws_group, aws_user))
