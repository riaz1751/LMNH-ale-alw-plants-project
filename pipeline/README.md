# Pipeline Overview
This pipeline will run an ETL script to:
- Extract plant data from an API endpoint.
- Clean, verify & transform the data.
- Load the data into a sql server database hosted on an AWS RDS


## Usage
```bash
python3 etl.py
```


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

# Extract 

## Features

- Fetches plant data from API endpoints
- Uses multi-threading for faster execution
- Automatically skips duplicates by checking last timestamps
- Uses logging for progress, updates and errors
- Loads all the data into a JSON file

## Requirements
```bash
pip3 install -r requirements.txt
```

## Configuration

Can change two parameters

- max_id (the number of plant IDs to check)
- workers (number of threads used)

## Usage 

Run the script

```bash
python3 extract.py
```

Then the script will:

- Loads existing plant data
- Finds the latest timestamp
- Fetches all the new records from the API
- Save all updates records back to plants.json


# Transform 

## Features

- Validates the required fields (plant_id, name, temperature, soil_moisture and recording_taken).
- Cleans the nested structures (Botanist data).
    - Get the name, email, phone.
    - Splits name into first and last.
- Validates email using regex.
- Phone number validation.
    - Supports extensions.
    - Converts dots to dashes.
- Title and suffix cleaning
    - Removes titles (Mr. Mrs. Dr. etc).
    - Removes suffixes (Jr. MD DVM).
- Timestamp normalisation.
- Drops unused fields like images.

## Requirements

pip3 install -r requirements.txt

## Usage

- python3 extract.py
- python3 transform.py

This will:

- Load the plant data from plants.json
- Validate and clean
- Print a preview of the cleaned data frame

## Transform steps

- Validate data types.
    - Drops images.
    - Convert name and scientific_name to string.
    - Standardise the timestamps: last_watered, recording_taken.
- Validate required columns.
    - Ensures plant_id and name are not null.
    - Ensures temperature and soil_moisture are not null.
    - Ensures recording_taken is not null.
- Clean botanist names.
    - Strip prefixes (Mr. Mrs. Ms. Dr.).
    - Strip suffixes (Jr. MD DVM and Roman numerals).
    - Split into first_name and last_name.
- Validate emails.
    - Regex check for valid format.
    - Drop rows with invalid emails.
- Validate and clean phone numbers.
    - Regex check for phone format (numbers, extensions).
    - Replaces '.' with '-'.
    - Drop rows with invalid phone numbers.


# Load

## Features

- Connects to the SQL Server RDS using pyodbc.
- Retrieves the plant data produced by the transform script.
- Loads data into the following tables in the schema beta:
    - Country (ensures the country names are unique).
    - City (ensures the city_name, city_id are unique).
    - Botanist (ensures the botanist email is unique).
    - Plant (ensures plant_name, city_id are unique).
    - Reading (inserts the valid readings and linked with plant_name and city_id).

## Table relationships

- Country: One country can have many cities.
- City: Linked to a single country.
- Botanist: Identified using unique email.
- Plant: Belongs to a city.
- Reading: Associated with both plant and botanist.

## Requirements

```bash
pip3 install -r requirements.txt
```

## Usage 

```bash
python3 load.py
```

This will:

- Connect to the RDS.
- Validate the existing mappings for country, city, plant and botanist.
- Insert new records only when they are unique enough.
- Add readings referencing the correct foreign keys.


