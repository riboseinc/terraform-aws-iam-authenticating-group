import json
import helper
import logging

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
        self.iam_groups_dict = {}
        self.__iam_groups = None
        self.__time_to_expire = None
        self.__logger = None

    @property
    def logger(self):
        if not self.__logger:
            self.__logger = logging.getLogger()
            self.__logger.setLevel(helper.get_catch(
                fn=lambda: int(logging.getLevelName("${log_level}")),
                default="INFO",
                ignore_result=False,
                ignore_error=True
            ))
        return self.__logger

    @property
    def iam_groups(self):
        if not self.__iam_groups:
            self.__iam_groups = helper.json_loads('''${iam_groups}''')
        return self.__iam_groups

    @iam_groups.setter
    def iam_groups(self, iam_groups):
        self.__iam_groups = iam_groups

    @property
    def time_to_expire(self):
        if self.__time_to_expire is None:
            self.__time_to_expire = helper.get_catch(
                fn=lambda: int("${time_to_expire}"),
                default=600,
                ignore_result=False,
                ignore_error=True
            )
        return self.__time_to_expire

    @time_to_expire.setter
    def time_to_expire(self, seconds):
        self.__time_to_expire = int(seconds)


arguments = Arguments()
