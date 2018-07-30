resource "template_dir" "this" {
  source_dir      = "${path.module}/src"
  destination_dir = "${path.module}/.src"

  vars {
    module_name    = "${var.module_name}"
    log_level      = "${var.log_level}"
    time_to_expire = "${var.time_to_expire}"
    bucket_name    = "${var.bucket_name}"
  }
}

data "archive_file" "service_py" {
  depends_on  = [
    "template_dir.this"
  ]
  type        = "zip"
  output_path = ".src.zip"
  source_dir  = "${template_dir.this.destination_dir}"
}
