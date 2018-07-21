import json
import helper
import logging
import boto3


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
    DEFAULT_EVENT = {
        "requestContext": {
            "identity": {
                "userArn": None
            }
        }
    }

    def __init__(self):
        self.event = Arguments.DEFAULT_EVENT
        self.iam_groups_dict = {}

        self.__iam_groups = None
        self.__time_to_expire = None
        self.__logger = None
        self.__module_name = None
        self.__api_caller = ""

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
    def iam_groups(self):
        if not self.__iam_groups:
            s3 = boto3.resource('s3')
            obj = s3.Object('${iam_groups_bucket}', 'args.json')
            json = obj.get()['Body'].read().decode('utf-8')
            self.__iam_groups = helper.json_loads(json)

        return self.__iam_groups

    @iam_groups.setter
    def iam_groups(self, iam_groups):
        self.__iam_groups = iam_groups

    @property
    def time_to_expire(self):
        if self.__time_to_expire is None:
            self.__time_to_expire = helper.get_default(fn=lambda: int("${time_to_expire}"), default=600)
        return self.__time_to_expire

    @time_to_expire.setter
    def time_to_expire(self, seconds):
        self.__time_to_expire = int(seconds)

    @property
    def api_caller(self):
        if self.event is not None and self.__api_caller is None:
            user_arn = self.event['requestContext']["identity"]["userArn"]
            if user_arn:
                self.__api_caller = user_arn.split("/")[-1]

        if self.__api_caller:
            return self.__api_caller

        return "system"


arguments = Arguments()
