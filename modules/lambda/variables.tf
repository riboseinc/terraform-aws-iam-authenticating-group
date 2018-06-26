variable "name" {}
variable "handler" {}
variable "source_code_path" {}
variable "source_code_hash" {}
variable "role_arn" {}
variable "description" {
  default = "created by terraform-aws-authenticating-iam"
}
