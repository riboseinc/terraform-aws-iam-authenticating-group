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
  stage_name  = "test"

//  access_log_settings {
//    destination_arn = "arn:aws:logs:us-west-2:239062223385:log-group:test:*"
//    format = "${replace(chomp(file("logformat.json")), "\n", "")}"
//  }
}

resource "aws_cloudwatch_log_group" "rest_api" {
//  depends_on = ["aws_api_gateway_rest_api.this"]
  name       = "${var.name}-${var.deployment_stage}"
//  arn = "${var.}"
//  name       = "API-Gateway-Execution-Logs_${aws_api_gateway_rest_api.this.id}/${var.deployment_stage}"
}

resource "aws_api_gateway_stage" "this" {
  deployment_id = "${aws_api_gateway_deployment.this.id}"
  rest_api_id   = "${aws_api_gateway_rest_api.this.id}"
  stage_name    = "${var.deployment_stage}"

  access_log_settings {
    destination_arn = "${aws_cloudwatch_log_group.rest_api.arn}"
//    destination_arn = "arn:aws:logs:us-west-2:239062223385:log-group:test:*"
    format = "${replace(chomp(local.api_log_format), "\n", "")}"
//    format = "${replace(chomp(file("logformat.json")), "\n", "")}"
  }
}

//resource "null_resource" "this" {
//
//////  depends_on = ["aws_cloudwatch_log_group.cloudwatch_access_log_group"]
//////  count = "${var.access_logs_enabled == "true" ? 1 : 0}"
//
////  triggers {
////    log_format = "${file("log_format.json")}"
////    log_group = "${local.cloudwatch_access_log_group_arn}"
////  }
//
//  provisioner "local-exec" {
////    command = "aws apigateway update-stage --rest-api-id ${aws_api_gateway_deployment.deployment.rest_api_id} --stage-name ${aws_api_gateway_deployment.deployment.stage_name} --patch-operations op=replace,path=/accessLogSettings/destinationArn,value='${local.cloudwatch_access_log_group_arn}'"
//    command = ""
//  }
//
////  provisioner "local-exec" {
////    command = "aws apigateway update-stage --rest-api-id ${aws_api_gateway_deployment.deployment.rest_api_id} --stage-name ${aws_api_gateway_deployment.deployment.stage_name} --patch-operations 'op=replace,path=/accessLogSettings/format,value=${jsonencode(replace(file("log_format.json"), "\n", ""))}'"
////  }
//
////  provisioner "local-exec" {
////    when = "destroy"
////    command = "aws apigateway update-stage --rest-api-id ${aws_api_gateway_deployment.deployment.rest_api_id} --stage-name ${aws_api_gateway_deployment.deployment.stage_name} --patch-operations op=remove,path=/accessLogSettings,value="
////  }
//}

resource "aws_api_gateway_account" "this" {
  cloudwatch_role_arn = "${module.sts_gateway.arn}"
}

//resource "aws_api_gateway_method_settings" "this" {
//  depends_on  = [
//    "aws_api_gateway_deployment.this",
//    "aws_api_gateway_account.this"
//  ]
//
//  rest_api_id = "${aws_api_gateway_rest_api.this.id}"
//  stage_name  = "${var.deployment_stage}"
//  method_path = "*/*"
//
//
////  settings {
////    metrics_enabled    = true
////    logging_level      = "INFO"
////    data_trace_enabled = true
////  }
//  settings {
//    metrics_enabled    = true
//    data_trace_enabled = true
//  }
//}

module "python" {
  source          = "modules/python"
  log_level = "${var.log_level}"
  iam_groups = "${var.iam_groups}"
  time_to_expire  = "${var.time_to_expire}"

  module_name     = ""
}

/**** check out "api_*.tf" ****/
