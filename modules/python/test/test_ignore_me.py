import boto3
import json
import helper
import botocore

from dateutil import parser
import logging

from datetime import datetime, timedelta
from dateutil import parser


# print(datetime.now())


# print(helper.json_loads('''
# ''[
#   {
#     "group_name": "test1",
#     "user_names": [
#       "phuonghqh1", "phuonghqh2"
#     ]
#   },
#   {
#     "group_name": "test2",
#     "user_names": [
#       "phuonghqh1", "phuonghqh2"
#     ]
#   }
# ]"
# '''))

# print(logging.getLevelName('DEBUG'))

# s = "arn:aws:s3:::expired-at-2018-04-10T23:11:42.089242+0700"
# print("expired-at-" in s)
# print(s[s.find("expired-at-") + len("expired-at-"):])
#
# print(str(parser.parse("2018-04-13T05:06:08.752194+0000")))

# ls = [
#     {
#         'name': {
#             'first': 'first',
#             'last': 'first'
#         }
#     },
#     {
#         'name': {
#             'first': 'first',
#             'last': 'last'
#         }
#     }
# ]
#
# lss = list(filter(lambda it: it['name'].get('last') == 'last', ls))
# print(lss)
#
# ls.remove(lss[0])
# print(ls)


# Create IAM client
# iam = boto3.resource('iam')
#
# try:
#     fake_policy = iam.GroupPolicy(group_name='test1', name='fake_policy')
#     fake_policy.load()
# except botocore.errorfactory.NoSuchEntityException:
#     pass



# Create Policy
# policy = { 'Version' : '2012-10-17'}
# policy['Statement'] = [{'Sid' : 'AwsIamUserPython',
#                         'Effect': 'Allow',
#                         'Action': "s3:GetObject",
#                         'Resource': 'arn:aws:s3:::phuongtestbucket/*'}]
# policy_json = json.dumps(policy)
#
# iam.put_user_policy('phuonghqh1', 'allow_access_class-rocks', policy_json)

# Create a policy
# my_managed_policy = {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Effect": "Allow",
#             "Action": [
#                 "s3:GetObject"
#             ],
#             "Resource": "arn:aws:s3:::fake/2018-04-05T00:00:00/*"
#         }
#     ]
# }


# response = iam.create_policy(
#   PolicyName='myDynamoDBPolicy3',
#   PolicyDocument=json.dumps(my_managed_policy)
# )
# print(response)

# Generate new access key pair for 'aws-user'
# key_response = iam.create_access_key('aws-user')

# dict1 = {'key': 123}
# dict2 = {'key': 123}
# dict3 = {'key': 12}
# print(helper.list_from_dict('key', dict1, dict2, dict3))
# ls=list({v['key']: v for v in [dict1, dict2, dict3]}.values())
# print(ls)
# str='hello'
# print(str[1:-1])
# print(json.loads(str))
# print(helper.json_loads('''
# {"key": 123}
# '''))
#
# print(helper.json_loads('''
# "{"key": 123}"
# '''))

# iam_client = boto3.client('iam')
# iam_client.add_user_to_group()

# iam = boto3.resource('iam')
# groups = list(iam.groups.all())
# for group in groups:
#     group.load()
#     print(group)
#     # group.users.objects.delete()
#     # users = group.users
#     u = iam.User(name='phuonghqh')
#     print(u)
    # users.append(u)
    # print(users)
# print(groups)


# for g in groups.all():
#     print(g)
# iam.Bucket('my-bucket').objects.delete()
