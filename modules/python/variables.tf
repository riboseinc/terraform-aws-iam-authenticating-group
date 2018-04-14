variable "log_level" {
  default = "INFO"
}

variable "iam_groups" {
  type    = "list"
  default = []
}

variable "time_to_expire" {
  default = ""
}

