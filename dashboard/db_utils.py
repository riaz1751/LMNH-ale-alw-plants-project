""" Provides a boto3 session ofr accessing AWS services using the credentials stored in 
the .env. 
get_connection() establishes the connection between RDS  using the credentials in the .env
query_db() executes a SQL query against the RDS
"""

import pandas as pd
import pyodbc
import boto3
from dotenv import load_dotenv
from os import environ as ENV

load_dotenv()


def boto3_session():
    """Create and return a boto3 session for extracting summary data from S3."""
    aws_session = boto3.Session(aws_access_key_id=ENV["AWS_ACCESS_KEY"],
                                aws_secret_access_key=ENV["AWS_SECRET_KEY"],
                                region_name=ENV["AWS_REGION"])
    return aws_session


def get_connection():
    """Create and return DB connection to RDS SQL Server."""
    conn_str = (f"DRIVER={{{ENV['DB_DRIVER']}}};SERVER={ENV['DB_HOST']};"
                f"PORT={ENV['DB_PORT']};DATABASE={ENV['DB_NAME']};"
                f"UID={ENV['DB_USERNAME']};PWD={ENV['DB_PASSWORD']};Encrypt=no;")
    return pyodbc.connect(conn_str)


def query_db(query: str) -> pd.DataFrame:
    """Run a query and return results as DataFrame."""
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df
