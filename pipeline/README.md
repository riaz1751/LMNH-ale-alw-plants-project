# Pipeline Overview
This pipeline will run an ETL script to:
- Extract plant data from an API endpoint.
- Clean, verify & transform the data.
- Load the data into a sql server database hosted on an AWS RDS


## Usage


## Requirements
1. An `.env` as follows
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
DB_SCHEMA = {db_schema}
```
2. A RDS hosting Sql Server, set up with `schema.sql`

```bash
sqlcmd -S [host],[port] -U [user] -P [password] -d [dbname] -i schema.sql
```