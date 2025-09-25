# Summary
This folder includes the entire workflow to summarise day old data from the RDS into an S3 Bucket for long-term storage.

## Requirements
1. A `.env` file formatted as below.
```ini

AWS_ACCESS_KEY={aws_access_key}
AWS_SECRET_ACCESS_KEY={aws_secret_access_key}
REGION={aws_region}
S3_BUCKET={s3_bucket_name}
DB_DRIVER
DB_HOST
DB_NAME
DB_PORT
DB_USERNAME
DB_PASSWORDDB_SCHEMA


```

# Extract

## Features

### Hourly Aggregates

```python
get_average_temp_df 
``` 

Calculates the average temperature of plants grouped by plant_id and hour

```python
get_average_soil_moisture_df
```

Calculates the average soil moisture of plants grouped by plant_id and hour

### Table retrievers

```python
get_plant_data_df
```

Retrieves all rows from the beta.Plant table

```python
get_reading_data_df
```

Retrieves all rows from the beta.Reading table

### Summarized data

```python
extract_data
```

Function for extracting and summarizing temperature and soil moisture from RDS

# Create Parquet

## Features

- Connects to the RDS SQL Server using connect_db_utils.
- Retrieves reading data so the beta.Reading table.
- Summarizes readings into hours using functions in extract:
    - get_average_temp_df - the hourly average plant temperature.
    - get_average_soil_moisture_df - the hourly average plant soil moisture.
- Exports both summaries into parquet format, and partitioned using the recording_taken.

## Usage

This script gets called by summary.py


# Connect_db_utils

## Features

### Get connection

```python
get_connection
```

Function to connect to the RDS database


### Query database

```python
query_db
```

Function to query the RDS database and return the response


### Clear reading table


```python
clear_reading_table
```

Function to clear the Reading table in the RDS


### Summary

## Features

- Connects to an RDS SQL Server database using credentials from the .env
- Extracts plant data using the extract_data function
- Creates parquet summaries partioned by date/time using the create_parquet function
- Uploads the parquet files to Amazon S3
- Clears the Reading table after success
- Can be executed as an AWS Lambda function

## Usage

```python
python3 summary.py
```

This will:

- Package the code and dependencies in a Docker image or Lambda layer
- Ensures the IAM is attatched to the Lambda 
- Uses logging so they are visible in CloudWatch
