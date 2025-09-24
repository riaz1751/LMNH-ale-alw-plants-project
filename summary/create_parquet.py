"""This script stores summary data in parquet files in an AWS S3 Bucket."""


import pandas as pd
from dotenv import load_dotenv
from os import getenv
import awswrangler as wr
import boto3
import pyodbc
from connect_db_utils import get_connection, query_db
from extract import get_average_soil_moisture_df, get_average_temp_df

def export_to_parquet(my_session: boto3.session.Session, conn: pyodbc.Connection, bucket: str):
    """upload summary data to parquet files in S3 bucket."""
    reading_data = pd.DataFrame.from_records(
        query_db(conn, "SELECT * FROM beta.Reading;"),
        columns=['reading_id', 'temperature', 'soil_moisture', 'recording_taken', 'plant_id', 'botanist_id']
    )

    reading_data["recording_taken"] = pd.to_datetime(
        reading_data["recording_taken"], errors="coerce"
    )

    avg_temp = get_average_temp_df(reading_data)
    avg_moisture = get_average_soil_moisture_df(reading_data)

    avg_temp["hour"] = avg_temp["recording_taken"]
    avg_moisture["hour"] = avg_moisture["recording_taken"]


    s3_path_temp = f"s3://{bucket}/etl-output/average_temperature/"
    s3_path_moist = f"s3://{bucket}/etl-output/average_soil_moisture/"

    wr.s3.to_parquet(
        df=avg_temp,
        path=s3_path_temp,
        dataset=True,
        partition_cols=["hour"],
        boto3_session=my_session,
        mode="overwrite"
    )

    wr.s3.to_parquet(
        df=avg_moisture,
        path=s3_path_moist,
        dataset=True,
        partition_cols=["hour"],
        boto3_session=my_session,
        mode="overwrite"
    )

    print(f"Data has been written to {s3_path_temp} and {s3_path_moist}")

if __name__ == "__main__":

    load_dotenv()

    conn = get_connection()
    
    my_session = boto3.session.Session(
        aws_access_key_id=getenv('AWS_ACCESS_KEY'), 
        aws_secret_access_key=getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=getenv('AWS_REGION')
        )
    bucket = getenv("S3_BUCKET")
        
    export_to_parquet(my_session, conn, bucket)

    conn.close()