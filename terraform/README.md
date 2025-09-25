# Terraform Set-up
This terraform script will set up all resources required for deploying the LMNH Project.

To setup initial resources, ECRs, S3, Glue DB, run `stage_one main.tf`. Once docker images are uploaded to the ECR, run `stage_two main.tf` to setup ECS Task Definitions, Lambda Functions, etc.


## Usage

1. Run stage_one main.tf with
```bash
# Inside stage_one folder
terraform apply
```
2. Push containerised images (ETL Pipeline & Summary pipeline) up to ECR, & put image URI in the associated resources in stage_two main.tf.

3. Run stage_two main.tf with
```bash
# Inside stage_two folder
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
DB_DRIVER= {db_driver}
```