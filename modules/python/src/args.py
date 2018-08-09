import json
import helper
import logging
import boto3
from os.path import basename, splitext


class Arguments:
    EXPIRED_AT = 'expired-at-%s'
    FAKE_POLICY_NAME = 'fake-policy-%s'
    FAKE_POLICY_DOC = json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "%s",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::%s"
            }
        ]
    })

    def __init__(self):
        self.__event = None
        self.__time_to_expire = None
        self.__logger = None
        self.__module_name = None

        self.api_caller = "SYSTEM"
        self.source_ip = None
        self.cidr_ip = None
        # self.__iam_groups = None

    @property
    def iam_groups(self):
        s3 = boto3.resource('s3')
        bucket = s3.Bucket('${bucket_name}')
        groups = []
        for s3_group in bucket.objects.all():
            users = helper.json_loads(s3_group.get()['Body'].read().decode('utf-8'))
            group_json_file = basename(s3_group.key)

            if not group_json_file.endswith('.json'):
                print(f'Object ${group_json_file} not endswith ".json" => ignore it')
                continue

            group_name = splitext(group_json_file)[0]
            groups.append({
                'group_name': group_name,
                'user_names': users
            })
        return groups

    @property
    def event(self):
        return self.__event

    @event.setter
    def event(self, event):
        try:
            self.__event = event

            user_arn = self.__event['requestContext']["identity"]["userArn"]
            if user_arn:
                self.api_caller = user_arn.split("/")[-1]

            self.source_ip = event['requestContext']['identity']['sourceIp']
            self.cidr_ip = f'{self.source_ip}/32'
        except (KeyError, AssertionError, TypeError) as error:
            print(f"Ignore error {str(error)}")

    @property
    def logger(self):
        if not self.__logger:
            self.__logger = logging.Logger(name=self.module_name)
            self.__logger.setLevel(helper.get_default(
                fn=lambda: int(logging.getLevelName("${log_level}")),
                default="INFO",
            ))

            handler = logging.StreamHandler()
            formatter = logging.Formatter(f"[%(levelname)s] [%(name)s] - %(message)s")
            handler.setFormatter(formatter)
            self.__logger.addHandler(handler)

        return self.__logger

    @property
    def module_name(self):
        if self.__module_name is None:
            self.__module_name = helper.get_default(fn=lambda: str("${module_name}"), default="dln")
        return self.__module_name

    @property
    def time_to_expire(self):
        if self.__time_to_expire is None:
            self.__time_to_expire = helper.get_default(fn=lambda: int("${time_to_expire}"), default=600)
        return self.__time_to_expire

    @time_to_expire.setter
    def time_to_expire(self, seconds):
        self.__time_to_expire = int(seconds)


arguments = Arguments()
