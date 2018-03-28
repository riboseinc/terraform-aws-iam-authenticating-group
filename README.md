# Terraform Module For Dynamically Managing IAM Groups

This module allows you to dynamically manage IAM group membership through an authenticated HTTPS endpoint.

This module is available on the [Terraform Registry](https://registry.terraform.io/modules/riboseinc/iam-authenticating-group)

### Components

    1. API Gateway that performs authorization.

    2. On-demand Lambda function (linked to API Gateway method `POST|DELETE /membership`): to add/remove IAM group memberships on-demand

    3. Continuous Lambda function: to clean up expired memberships


### On-demand Lambda Function: Adding/Removing IAM Group Membership

This is the Lambda function that runs `add-user-to-group` and
`remove-user-from-group` on-demand on the given IAM group.

Steps:

    1.  Authenticate the user via AWS IAM (Signature Version 4).
        Eligibility to authenticate is set in a policy outside of this module.
        The user will provide an AWS v4 signature for authentication.
        Return **403** if not authorized.

    3. If the request is a `POST /membership`
        -   The function will issue a `add-user-to-group` action for the
            user, with a description that indicates the "time" that this membership
            was added.
            Return **201**.
        -   If the user is already in the IAM group,
            (TODO: How to find out the time user was added?)
            Return **200**

    4. If the request is a `DELETE /membership`
        -   If the user is in the IAM group, issue a `remove-user-from-group` on it. Return **200**.
        -   If the user is not in the IAM group, do nothing. Return **404**.

    3. Done.

### Continuous Lambda Function: Removing Rules

This is the Lambda function that runs `remove-user-from-group` on the
given IAM group on user access expiry.

This AWS Lambda function runs every X seconds, and its sole task is to clean
out the IAM group that has stale membership.

Steps:

    1. The function will describe all rules in the given security group.

    2. For every rule, it will check the description for the time of last update.
        -   If the elapsed time is less than the configured X seconds, don't do anything.
        -   If the elapsed time is more than the configured X seconds, it means that the
            rule has expired, and it should execute `revoke-security-group-ingress` on it.
            (e.g., if all rules are expired, the security group should now contain no rules)

    3. Done.


### Sample Usage

Check out [examples](https://github.com/riboseinc/terraform-aws-iam-authenticating-group/tree/master/examples) for more details

```terraform
/* where should this API deployed to, more info https://www.terraform.io/docs/providers/aws */
provider "aws" {
  region  = "us-west-2"
}

/* main configuration */
module "dynamic-iamgroup" {
  source = "riboseinc/iam-authenticating-group/aws"

  name            = "example-terraform-aws-iam-authenticating-group"

  # Description of this IAM group
  description     = "example usage of terraform-aws-iam-authenticating-group"

  //  # Time to expiry for every membership.
  time_to_expire  = 600

  providers = {

  }
  groups = [
    {
      "group_names"   = [
        "group1",
        "group2"
      ],
      "region_name" = "us-west-1"
    },
    {
      "group_names"   = [
        "group3"
      ],
      "region_name" = "us-west-2"
    }
  ]
}

/* policy */
resource "aws_iam_policy" "this" {
  description = "Policy Developer SSH Access"
  policy      = "${data.aws_iam_policy_document.access_policy_doc.json}"
}

data "aws_iam_policy_document" "access_policy_doc" {
  statement {
    effect    = "Allow"
    actions   = [
      "execute-api:Invoke"
    ]
    resources = [
      "${module.dynamic-iamgroup.execution_resources}"]
  }
}

/** Some outputs */

output "dynamic-iamgroup-api-invoke-url" {
  value = "${module.dynamic-iamgroup.invoke_url}"
}
```


### Bash to execute the API

Check out [aws-authenticating-secgroup-scripts](https://github.com/riboseinc/aws-iam-authenticating-group-scripts)

