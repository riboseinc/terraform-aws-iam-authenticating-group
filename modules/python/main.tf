resource "template_dir" "this" {
  source_dir      = "${path.module}/src"
  destination_dir = "${path.module}/.archive"

  vars {
    module_name = "${var.module_name}"
    log_level  = "${var.log_level}"
    iam_groups = "${jsonencode(var.iam_groups)}"
    time_to_expire  = "${var.time_to_expire}"
  }
}

data "archive_file" "service_py" {
  depends_on  = [
    "template_dir.this"
  ]
  type        = "zip"
  output_path = "${path.module}/.archive.zip"
  source_dir  = "${template_dir.this.destination_dir}"
}
