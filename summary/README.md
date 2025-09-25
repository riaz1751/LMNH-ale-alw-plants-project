### Summary

## Environment variables

```ini

Fill in with environment variables
AWS_ACCESS_KEY
AWS_SECRET_ACCESS_KEY
AWS_REGION
S3_BUCKET

```

### Extract

## Features

# Hourly Aggregates

```python
get_average_temp_df 
``` 

Calculates the average temperature of plants grouped by plant_id and hour

```python
get_average_soil_moisture_df
```

Calculates the average soil moisture of plants grouped by plant_id and hour

# Table retrievers

```python
get_plant_data_df
```

Retrieves all rows from the beta.Plant table

```python
get_reading_data_df
```

Retrieves all rows from the beta.Reading table

# Summarized data

```python
extract_data
```

Function for extracting and summarizing temperature and soil moisture from RDS

### Create Parquet

## Features

- Connects to the RDS SQL Server using connect_db_utils
- Retrieves reading data so the beta.Reading table
- Summarizes readings into hours using functions in extract:
    - get_average_temp_df - the hourly average plant temperature
    - get_average_soil_moisture_df - the hourly average plant soil moisture
- Exports both summaries into parquet format, and partitioned using the recording_taken

## Usage

This script gets called by summary.py


## Connect_db_utils

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

