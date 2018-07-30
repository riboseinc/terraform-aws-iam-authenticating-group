variable "module_name" {}
variable "bucket_name" {}
variable "log_level" {}

variable "iam_groups" {
  type    = "list"
  default = []
}

variable "time_to_expire" {
  default = ""
}

