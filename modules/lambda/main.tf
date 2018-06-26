resource "aws_cloudwatch_log_group" "this" {
  name       = "/aws/lambda/${var.name}"
}

resource "aws_lambda_function" "this" {
  depends_on = ["aws_cloudwatch_log_group.this"]
  description      = "${var.description}"
  role             = "${var.role_arn}"
  runtime          = "python3.6"

  filename         = "${var.source_code_path}"
  source_code_hash = "${var.source_code_hash}"

  function_name    = "${var.name}"
  handler          = "${var.handler}"

  timeout          = "300" # ~5mins

  lifecycle {
    ignore_changes = [
      "source_code_hash",
      "last_modified"
    ]
  }
}
