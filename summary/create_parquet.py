import pandas as pd
from dotenv import load_dotenv
from connect_db_utils import get_connection, query_db
from extract import get_average_soil_moisture_df, get_average_temp_df

def export_to_parquet():
    load_dotenv()
    conn = get_connection()

    reading_data = pd.DataFrame.from_records(
        query_db(conn, "SELECT * FROM beta.Reading;"),
        columns=['reading_id', 'temperature', 'soil_moisture', 'recording_taken', 'plant_id', 'botanist_id']
    )

    avg_temp = get_average_temp_df(reading_data)
    avg_moisture = get_average_soil_moisture_df(reading_data)

    avg_temp.to_parquet("average_temperature",
                        partition_cols=["recording_taken"],
                        index=False)
    avg_moisture.to_parquet("average_soil_moisture", 
                        partition_cols=["recording_taken"],
                        index=False)

    print("It worked")

    conn.close()

if __name__ == "__main__":
    export_to_parquet()