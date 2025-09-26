### Plant monitoring dashboard

Provides a Streamlit dashboard for monitoring and comparing plant sensor data such as
temperature and soil moisture. Supports data from historical summaries (S3) and live
sensor readings (RDS)

## Features

- Compare the temparture vs soil moisture over time
- Filter data by plant name and ID
- Switch between Athena and RDS live data
- Cached queries for faster dashboard performance

## Requirements

```python
pip3 install -r requirements.txt
```

## Environment Variables

```ini
# AWS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=eu-west-2
S3_BUCKET=your_s3_bucket

# Athena
ATHENA_DATABASE=c19-cran-plants-db
ATHENA_OUTPUT=s3://your-athena-query-results/

# RDS
RDS_SERVER=your-rds-endpoint
RDS_DATABASE=plants_db
RDS_USER=your_user
RDS_PASSWORD=your_password
```

## Usage

- Choose data source so either RDS or S3
- Filter by plant name or ID
- Explore the charts
    - Temperature vs Soil Moisture scatterplot
    - Time series for temperature
    - Time series for soil moisture