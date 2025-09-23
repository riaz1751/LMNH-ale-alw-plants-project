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
REGION={region}
S3_NAME={bucket_name}
DB_HOST={db_host}
DB_PORT={db_port}
DB_NAME={db_name}
DB_USERNAME={db_username}
DB_PASSWORD={db_password}
```