provider "aws" {
  region = "us-west-2"
}

module "dynamic-iam-group" {
  source         = "../../"
  name           = "example-dynamic-iam-groups"
  bucket_name    = "example-dynamic-iam-groups-bucket"
  description    = "example usage of terraform-aws-authenticating-iam"
  time_to_expire = 300
  log_level = "DEBUG"
  iam_groups     = [
    {
      "group_name" = "test1",
      "user_names" = [
        "phuonghqh1",
        "phuonghqh2"
      ]
    },
    {
      "group_name" = "test2",
      "user_names" = [
        "phuonghqh1",
        "phuonghqh2"
      ]
    }
  ]
}

resource "aws_iam_policy" "this" {
  description = "Policy Developer IAM Access"
  policy      = "${data.aws_iam_policy_document.access_policy_doc.json}"
}

data "aws_iam_policy_document" "access_policy_doc" {
  statement {
    effect    = "Allow"
    actions   = [
      "execute-api:Invoke"
    ]
    resources = [
      "${module.dynamic-iam-group.execution_resources}"
    ]
  }
}

output "dynamic-secgroup-api-invoke-url" {
  value = "${module.dynamic-iam-group.invoke_url}"
}
