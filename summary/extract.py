"""Extract data from RDS to create summaries"""

from connect_db_utils import get_connection, query_db
from dotenv import load_dotenv
import pandas as pd
import pyodbc
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def get_average_temp_df(reading_df: pd.DataFrame) -> pd.DataFrame:
    """Get a dataframe of the average temperature of all plants by the hour"""
    return reading_df.groupby(['plant_id', 'year', 'month', 'day', 'hour'])['temperature'].mean().reset_index(name='average_temperature')


def get_average_soil_moisture_df(reading_df: pd.DataFrame) -> pd.DataFrame:
    """Get a dataframe of the average soilMoisture of all plants by the hour"""
    return reading_df.groupby(['plant_id', 'year', 'month', 'day', 'hour'])['soil_moisture'].mean().reset_index(name='average_soil_moisture')


def get_plant_data_df(conn) -> pd.DataFrame:
    """Get all the plant table data form the RDS"""
    return pd.DataFrame.from_records(query_db(conn, "SELECT * FROM beta.Plant;"),
                                     columns=['plant_id', 'plant_name', 'scientific_name', 'last_watered', 'city_id'])


def get_reading_data_df(conn) -> pd.DataFrame:
    """Get all the reading table data form the RDS"""
    reading_df = pd.DataFrame.from_records(query_db(conn, "SELECT * FROM beta.Reading;"),
                                           columns=['reading_id', 'temperature', 'soil_moisture', 'recording_taken', 'plant_id', 'botanist_id'])
    reading_df['year'] = reading_df['recording_taken'].dt.year
    reading_df['month'] = reading_df['recording_taken'].dt.month
    reading_df['day'] = reading_df['recording_taken'].dt.day
    reading_df['hour'] = reading_df['recording_taken'].dt.hour

    return reading_df


def get_summary_data_df(temperature_df, soil_moisture_df) -> pd.DataFrame:
    """Get a dataframe containing all the necessary summary data."""
    summary_df = temperature_df
    summary_df["average_soil_moisture"] = soil_moisture_df["average_soil_moisture"]
    logging.info("Reading data successfully summarised.")
    return summary_df


def extract_data(conn: pyodbc.Connection) -> pd.DataFrame:
    """Extracts and summarises reading data, temp data, & soil moisture data."""

    logging.info("Extracting reading data from database.")
    reading_df = get_reading_data_df(conn)

    temp_df = get_average_temp_df(reading_df)

    soil_moisture_df = get_average_soil_moisture_df(reading_df)

    return get_summary_data_df(temp_df, soil_moisture_df)


if __name__ == "__main__":

    load_dotenv()

    conn = get_connection()

    reading_df = get_reading_data_df(conn)

    temp_df = get_average_temp_df(reading_df)

    soil_moisture_df = get_average_soil_moisture_df(reading_df)

    get_summary_data_df(temp_df, soil_moisture_df)

    conn.close()
