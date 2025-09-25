"""This script stores summary data in parquet files in an AWS S3 Bucket."""


import pandas as pd
from dotenv import load_dotenv
from os import getenv
import awswrangler as wr
import boto3
import pyodbc
import logging
from connect_db_utils import get_connection, query_db, clear_reading_table
from extract import get_reading_data_df, get_average_soil_moisture_df, get_average_temp_df, get_summary_data_df

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def export_to_parquet(my_session: boto3.session.Session, conn: pyodbc.Connection, bucket: str, summary_data_df: pd.DataFrame):
    """Upload summary data to parquet files in S3 bucket."""

    s3_path_summary = f"s3://{bucket}/summary/"

    wr.s3.to_parquet(
        df=summary_data_df,
        path=s3_path_summary,
        dataset=True,
        partition_cols=["year", "month", "day", "hour"],
        boto3_session=my_session,
        mode="overwrite"
    )
    logging.info(f"Data has been written to {s3_path_summary}")
    

def create_parquet(conn: pyodbc.Connection, summary_df: pd.DataFrame):
    """Script to run the entire parquet workflow."""

    my_session = boto3.session.Session(
        aws_access_key_id=getenv('ACCESS_KEY'),
        aws_secret_access_key=getenv('SECRET_ACCESS_KEY'),
        region_name=getenv('REGION')
    )
    bucket = getenv("S3_BUCKET")

    export_to_parquet(my_session, conn, bucket, summary_df)
    
if __name__ == "__main__":
    load_dotenv()

    conn = get_connection()

    create_parquet(conn)
    clear_reading_table(conn)

    conn.close()