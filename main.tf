locals {
  authorize_fn_name     = "authorize-${var.name}"
  authorize_http_method = "POST"

  revoke_fn_name        = "revoke-${var.name}"
  revoke_http_method    = "DELETE"

  clear_fn_name         = "clear-${var.name}"
  clear_event_rule_name = "clear-expired-${var.name}"
  clear_event_rate      = "rate(1 minute)"

  api_log_format = <<EOF
    {
      "requestId": "$context.requestId",
      "ip": "$context.identity.sourceIp",
      "caller": "$context.identity.caller",
      "user": "$context.identity.user",
      "requestTime": "$context.requestTime",
      "httpMethod": "$context.httpMethod",
      "resourcePath": "$context.resourcePath",
      "status": "$context.status",
      "protocol": "$context.protocol",
      "responseLength": "$context.responseLength"
    }
  EOF
}

resource "aws_api_gateway_rest_api" "this" {
  name        = "${var.name}"
  description = "${var.description}"
}

resource "aws_api_gateway_resource" "this" {
  rest_api_id = "${aws_api_gateway_rest_api.this.id}"
  parent_id   = "${aws_api_gateway_rest_api.this.root_resource_id}"
  path_part   = "membership"
}

resource "aws_api_gateway_deployment" "this" {
  depends_on  = [
    "module.gateway_authorize",
    "module.gateway_revoke"
  ]

  rest_api_id = "${aws_api_gateway_rest_api.this.id}"
  stage_name  = ""
}

resource "aws_cloudwatch_log_group" "rest_api" {
  name       = "${var.name}-${var.deployment_stage}"
}

resource "aws_api_gateway_stage" "this" {
  deployment_id = "${aws_api_gateway_deployment.this.id}"
  rest_api_id   = "${aws_api_gateway_rest_api.this.id}"
  stage_name    = "${var.deployment_stage}"

  access_log_settings {
    destination_arn = "${aws_cloudwatch_log_group.rest_api.arn}"
    format = "${replace(chomp(local.api_log_format), "\n", "")}"
  }
}

resource "aws_api_gateway_account" "this" {
  cloudwatch_role_arn = "${module.sts_gateway.arn}"
}

resource "aws_api_gateway_method_settings" "this" {
  depends_on  = [
    "aws_api_gateway_deployment.this",
    "aws_api_gateway_account.this"
  ]

  rest_api_id = "${aws_api_gateway_rest_api.this.id}"
  stage_name  = "${var.deployment_stage}"
  method_path = "*/*"

  settings {
    metrics_enabled    = true
    data_trace_enabled = true
  }
}

module "python" {
  source          = "modules/python"
  log_level = "${var.log_level}"
  iam_groups = "${var.iam_groups}"
  time_to_expire  = "${var.time_to_expire}"
  module_name     = "${var.name}"
}

//data "aws_s3_bucket" "this" {
//  bucket = "terraform-aws-iam-authenticating-group"
//}

//data "aws_s3_bucket_object" "bootstrap_script" {
//  bucket = "terraform-aws-iam-authenticating-group"
//  key    = "ec2-bootstrap-script.sh"
//}

//data "template_file" "init" {
//  template = "${file("${path.module}/init.tpl")}"
//
//  vars {
//    consul_address = "${aws_instance.consul.private_ip}"
//  }
//}

resource "local_file" "foo" {
  content     = "${jsonencode(var.iam_groups)}"
  filename = "${path.module}/iam_groups.json"
}


resource "aws_s3_bucket" "this" {
  bucket = "${var.name}"
  acl    = "private"

/*
  tags {
    Name        = "My bucket"
    Environment = "Dev"
  }
*/
}


resource "aws_s3_bucket_object" "this" {
  bucket = "${aws_s3_bucket.this.bucket}"
//  bucket = "${data.aws_s3_bucket.this.bucket}"
  key = "args.json"
  source = "${path.module}/iam_groups.json"
//  content_type = "text/html"
//  etag = "${md5(file("src/index.html"))}"
}

/**** check out "api_*.tf" ****/
