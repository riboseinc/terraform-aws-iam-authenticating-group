module "sts_lambda" {
  source = "modules/sts_assume_role"

  service_identifier = "lambda.amazonaws.com"
  name = "${var.name}-lambda"
  actions = [
    "iam:DeleteUserPolicy",
    "iam:PutUserPolicy",
    "iam:GetUser",
    "iam:GetGroup",
    "iam:AddUserToGroup",
    "iam:RemoveUserFromGroup",
    "iam:GetUserPolicy",

    "s3:GetBucketLocation",
    "s3:ListBucket",
    "s3:GetObject",

    "logs:CreateLogGroup",
    "logs:CreateLogStream",
    "logs:PutLogEvents"
  ]
  description = "used by Lambda"
}

module "sts_gateway" {
  source = "modules/sts_assume_role"

  service_identifier = "apigateway.amazonaws.com"
  name = "${var.name}-gateway"
  actions = [
    "logs:CreateLogGroup",
    "logs:CreateLogStream",
    "logs:DescribeLogGroups",
    "logs:DescribeLogStreams",
    "logs:PutLogEvents",
    "logs:GetLogEvents",
    "logs:FilterLogEvents"
  ]
  description = "used by API Gateway to write log (CloudWatch)"
}
