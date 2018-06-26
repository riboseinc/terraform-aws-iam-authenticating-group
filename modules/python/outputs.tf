output "output_path" {
  value = "${data.archive_file.service_py.output_path}"
}

output "output_base64sha256" {
  value = "${local.vars_base64sha256}"
}

output "authorize_handler" {
  value = "authorize.handler"
}

output "revoke_handler" {
  value = "revoke.handler"
}

output "clear_handler" {
  value = "clear.handler"
}
