"""Utility functions for connecting to the RDS SQL Server."""
from os import environ as ENV

from dotenv import load_dotenv
import pyodbc


def get_connection() -> pyodbc.Connection:
    """Return a connection to the RDS."""
    conn_str = (f"DRIVER={{{ENV['DB_DRIVER']}}};SERVER={ENV['DB_HOST']};"
                f"PORT={ENV['DB_PORT']};DATABASE={ENV['DB_NAME']};"
                f"UID={ENV['DB_USERNAME']};PWD={ENV['DB_PASSWORD']};Encrypt=no;")

    return pyodbc.connect(conn_str)


def query_db(conn: pyodbc.Connection, query: str) -> list:
    """Queries the DB and returns the response."""
    with conn.cursor() as cur:
        cur.execute(query)
        data = cur.fetchall()
    return data


def insert_db(conn: pyodbc.Connection, query: str):
    """Inserts row into DB"""
    with conn.cursor() as cur:
        cur.execute(query)


def get_mapping(conn: pyodbc.Connection, table_name: str, attr: str, primary_key: str) -> dict:
    """Returns a mapping between attr & primary key for transformation mapping."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT {attr}, {primary_key} from {table_name};")
        data = cur.fetchall()
    return {row[0]: row[1] for row in data}


if __name__ == "__main__":

    load_dotenv()

    conn = get_connection()

    conn.close()
