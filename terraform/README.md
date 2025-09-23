# Terraform Set-up
This terraform script will set up all resources required for the LMNH Project to run.


## Usage

Run with
```bash
terraform apply
```

## Requirements
1. A `terraform.tfvars` as follows
```ini
ACCESS_KEY={your_aws_key}
SECRET_ACCESS_KEY={your_aws_secret_key}
```