"""Utility functions for connecting to the RDS SQL Server."""
from os import environ as ENV

from dotenv import load_dotenv
import pyodbc
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def get_connection() -> pyodbc.Connection:
    """Return a connection to the RDS."""
    conn_str = (f"DRIVER={{{ENV['DB_DRIVER']}}};SERVER={ENV['DB_HOST']};"
                f"PORT={ENV['DB_PORT']};DATABASE={ENV['DB_NAME']};"
                f"UID={ENV['DB_USERNAME']};PWD={ENV['DB_PASSWORD']};Encrypt=no;")

    return pyodbc.connect(conn_str)


def query_db(conn: pyodbc.Connection, query: str):
    """Queries the DB and returns the response."""
    with conn.cursor() as cur:
        cur.execute(query)
        data = cur.fetchall()
    return data


def clear_reading_table(conn: pyodbc.Connection):
    """Clear the reading table from the plants database."""
    logging.info("Deleting data from RDS.")
    with conn.cursor() as cur:
        cur.execute("DELETE FROM beta.Reading;")
        conn.commit()

if __name__ == "__main__":

    load_dotenv()

    conn = get_connection()

    print(query_db(conn, "SELECT * FROM beta.City;"))

    conn.close()
