from create_parquet import create_parquet
from extract import extract_data
from connect_db_utils import get_connection, clear_reading_table
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

def handler(event=None, context=None):
    """AWS Lambda Handler for summary pipeline"""
    logging.info("Starting summary pipeline.")
    load_dotenv()
    conn = get_connection()

    summary_df = extract_data(conn)
    create_parquet(conn, summary_df)
    clear_reading_table(conn)

    conn.close()
    logging.info("Finishing summary pipeline.")
    
if __name__ == "__main__":
    load_dotenv()
    conn = get_connection()

    summary_df = extract_data(conn)
    create_parquet(conn, summary_df)
    clear_reading_table(conn)

    conn.close()