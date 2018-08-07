locals {
  authorize_fn_name     = "authorize-${var.name}"
  authorize_http_method = "POST"

  revoke_fn_name        = "revoke-${var.name}"
  revoke_http_method    = "DELETE"

  clear_fn_name         = "clear-${var.name}"
  clear_event_rule_name = "clear-expired-${var.name}"
  clear_event_rate      = "rate(1 minute)"

  api_log_format        = <<EOF
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
  name = "${var.name}-${var.deployment_stage}"
}

resource "aws_api_gateway_stage" "this" {
  deployment_id = "${aws_api_gateway_deployment.this.id}"
  rest_api_id   = "${aws_api_gateway_rest_api.this.id}"
  stage_name    = "${var.deployment_stage}"

  access_log_settings {
    destination_arn = "${aws_cloudwatch_log_group.rest_api.arn}"
    format          = "${replace(chomp(local.api_log_format), "\n", "")}"
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
  source         = "modules/python"
  log_level      = "${var.log_level}"
  time_to_expire = "${var.time_to_expire}"
  module_name    = "${var.name}"
  bucket_name    = "${var.bucket_name}"
//  iam_group      = "${var.iam_group}"
}

//resource "local_file" "foo" {
//  content  = "${jsonencode(var.iam_users)}"
//  filename = "${path.module}/iam_groups.json"
//}

//resource "aws_s3_bucket" "this" {
//  bucket = "${var.bucket_name}"
//  acl    = "private"
//}

//resource "aws_s3_bucket_object" "this" {
//  count = "${length(var.iam_groups)}"
//  bucket = "${aws_s3_bucket.this.bucket}"
//  key    = "${element(var.iam_groups, count.index)}"
//  source = "${element(var.iam_groups, count.index)}"
//}

/**** check out "api_*.tf" ****/
