"""Extract data from RDS to create summaries"""

from connect_db_utils import get_connection, query_db
from dotenv import load_dotenv
import pandas as pd

# hourly data
# plant name
# average temp
# average soil moisture

def get_average_temp_df(reading_df: pd.DataFrame) -> pd.DataFrame:
    """Get a dataframe of the average temperature of all plants by the hour"""
    return reading_df.groupby(['plant_id', reading_df['recording_taken'].dt.hour])['temperature'].mean().reset_index(name='average_temperature')
 

def get_average_soil_moisture_df(reading_df: pd.DataFrame) -> pd.DataFrame:
    """Get a dataframe of the average soilMoisture of all plants by the hour"""
    return reading_df.groupby(
        ['plant_id', reading_df['recording_taken'].dt.hour])['soil_moisture'].mean().reset_index(name='average_soil_moisture')


def get_plant_data_df(conn) -> pd.DataFrame:
    """Get all the plant table data form the RDS"""
    return pd.DataFrame.from_records(query_db(conn, "SELECT * FROM beta.Plant;"),
                                     columns=['plant_id', 'plant_name', 'scientific_name', 'last_watered', 'city_id'])


def get_reading_data_df(conn) -> pd.DataFrame:
    """Get all the reading table data form the RDS"""
    return pd.DataFrame.from_records(query_db(conn, "SELECT * FROM beta.Reading;"),
                                     columns=['reading_id', 'temperature', 'soil_moisture', 'recording_taken', 'plant_id', 'botanist_id'])


