import pandas as pd
import pyodbc
from dotenv import load_dotenv
from os import environ as ENV

load_dotenv()


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
