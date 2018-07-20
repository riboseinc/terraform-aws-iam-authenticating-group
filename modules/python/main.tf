//locals {
//  vars_base64sha256    = "${base64sha256(join("-",list(
//      var.module_name,
//      jsonencode(var.iam_groups),
//      var.log_level,
//      var.time_to_expire
//  )))}"
//  destination_dir = "${path.module}/.src-${local.vars_base64sha256}"
//}

resource "template_dir" "this" {
  source_dir      = "${path.module}/src"
  destination_dir = "${path.module}/.src"
//  destination_dir = "${local.destination_dir}"

  vars {
    module_name    = "${var.module_name}"
    log_level      = "${var.log_level}"
//    iam_groups     = "${jsonencode(var.iam_groups)}"
    time_to_expire = "${var.time_to_expire}"
    iam_groups_bucket = "${var.module_name}"
  }
}

data "archive_file" "service_py" {
  depends_on  = [
    "template_dir.this"
  ]
  type        = "zip"
//  output_path = "${local.destination_dir}.zip"
  output_path = ".src.zip"
  source_dir  = "${template_dir.this.destination_dir}"
}
