"""Extract data from RDS to create summaries"""

from connect_db_utils import get_connection, query_db
from dotenv import load_dotenv
import pandas as pd

# hourly data
# plant name
# average temp
# average soil moisture



if __name__ == "__main__":
    
    load_dotenv()

    conn = get_connection()

    city_data_df = pd.DataFrame.from_records(query_db(conn, "SELECT * FROM beta.City;"),
                              columns=['city_id', 'city_name', 'lat', 'long', 'country_id'])
    country_data_df = pd.DataFrame.from_records(query_db(conn, "SELECT * FROM beta.Country;"),
                              columns=['country_id', 'country_name'])
    plant_data_df = pd.DataFrame.from_records(query_db(conn, "SELECT * FROM beta.City;"),
                              columns=['plant_id', 'plant_name', 'scientific_name', 'last_watered', 'city_id'])
    botanist_data_df = pd.DataFrame.from_records(query_db(conn, "SELECT * FROM beta.City;"),
                              columns=['botanist_id', 'first_name', 'last_name', 'email', 'phone_number'])
    reading_data_df = pd.DataFrame.from_records(query_db(conn, "SELECT * FROM beta.City;"),
                              columns=['reading_id', 'temperature', 'soil_moisture', 'recording_taken', 'plant_id', 'botanist_id'])
    
    average_temp_df = reading_data_df.groupby(['plant_id', reading_data_df['recording_taken'].dt.hour])['temperature'].mean()

    average_soil_moisture_df = reading_data_df.groupby(
        ['plant_id', reading_data_df['recording_taken'].dt.hour])['soil_moisture'].mean()


    conn.close()
