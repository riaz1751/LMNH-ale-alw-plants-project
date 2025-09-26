"""Utility functions for connecting to the RDS SQL Server."""

import pyodbc
from os import environ as ENV
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Load environment variables from .env
load_dotenv()


def get_connection() -> pyodbc.Connection:
    """Return a connection to the RDS SQL Server."""
    conn_str = (
        f"DRIVER={{{ENV['DB_DRIVER']}}};"
        f"SERVER={ENV['DB_HOST']};"
        f"PORT={ENV['DB_PORT']};"
        f"DATABASE={ENV['DB_NAME']};"
        f"UID={ENV['DB_USERNAME']};"
        f"PWD={ENV['DB_PASSWORD']};"
        "Encrypt=no;"
    )
    return pyodbc.connect(conn_str)


def query_db(conn: pyodbc.Connection, query: str):
    """Run a SQL query and return all rows."""
    with conn.cursor() as cur:
        cur.execute(query)
        data = cur.fetchall()
    return data


def clear_table(conn: pyodbc.Connection, table_name: str):
    """Delete all rows from a given table."""
    logging.info(f"Clearing table {table_name} in RDS.")
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM {table_name};")
        conn.commit()


if __name__ == "__main__":
    conn = get_connection()
    print(query_db(conn, "SELECT TOP 5 * FROM beta.Country;"))
    conn.close()
