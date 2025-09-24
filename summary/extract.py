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



if __name__ == "__main__":
    
    load_dotenv()

    conn = get_connection()

    # city_data_df = pd.DataFrame.from_records(query_db(conn, "SELECT * FROM beta.City;"),
    #                           columns=['city_id', 'city_name', 'lat', 'long', 'country_id'])
    # country_data_df = pd.DataFrame.from_records(query_db(conn, "SELECT * FROM beta.Country;"),
    #                           columns=['country_id', 'country_name'])
    # plant_data_df = pd.DataFrame.from_records(query_db(conn, "SELECT * FROM beta.Plant;"),
    #                           columns=['plant_id', 'plant_name', 'scientific_name', 'last_watered', 'city_id'])
    # botanist_data_df = pd.DataFrame.from_records(query_db(conn, "SELECT * FROM beta.Botanist;"),
    #                           columns=['botanist_id', 'first_name', 'last_name', 'email', 'phone_number'])
    # reading_data_df = pd.DataFrame.from_records(query_db(conn, "SELECT * FROM beta.Reading;"),
    #                           columns=['reading_id', 'temperature', 'soil_moisture', 'recording_taken', 'plant_id', 'botanist_id'])

    plant_data_df = get_plant_data_df(conn)
    reading_data_df = get_reading_data_df(conn)
    
    average_temp_df = get_average_temp_df(reading_data_df)
    average_soil_moisture_df = get_average_soil_moisture_df(reading_data_df)

    conn.close()
