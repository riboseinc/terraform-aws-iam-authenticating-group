provider "aws" {
  region = "us-west-2"
}

locals {
  bucket_name = "example-dynamic-iam-groups-bucket",
  iam_groups = ["test1.json", "test2.json"]
}

resource "aws_s3_bucket" "this" {
  bucket = "${local.bucket_name}"
  acl    = "private"
}

resource "aws_s3_bucket_object" "this" {
  count = "${length(local.iam_groups)}"
  bucket = "${aws_s3_bucket.this.bucket}"
  key    = "${element(local.iam_groups, count.index)}"
  source = "${element(local.iam_groups, count.index)}"
}


module "dynamic-iam-group" {
  source         = "../../"
  name           = "example-dynamic-iam-groups"
  bucket_name    = "${local.bucket_name}"
  description    = "example usage of terraform-aws-authenticating-iam"
  time_to_expire = 300
  log_level = "DEBUG"
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
