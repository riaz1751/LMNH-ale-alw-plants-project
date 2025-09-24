"""Load transformed plant data into the database."""
import logging
import pandas as pd
from transform import clean_valid_data
from connect_db_utils import get_connection, insert_db, get_mapping

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def load_data():
    conn = get_connection()

    # Load transformed dataframe
    data: pd.DataFrame = clean_valid_data()

    # Load Countries
    logging.info("Loading countries")
    for country in data["origin_location"].apply(lambda x: x.get("country")).unique():
        insert_db(
            conn,
            "INSERT INTO beta.Country (country_name) VALUES (?)",
            (country,),
        )

    country_map = get_mapping(conn, "beta.Country",
                              "country_name", "country_id")

    # Load Cities
    logging.info("Loading cities")
    for _, row in data.iterrows():
        insert_db(
            conn,
            """
            INSERT INTO beta.City (city_name, lat, long, country_id)
            VALUES (?, ?, ?, ?)
            """,
            (
                row["origin_location"]["city"],
                row["origin_location"]["latitude"],
                row["origin_location"]["longitude"],
                country_map[row["origin_location"]["country"]],
            ),
        )

    city_map = get_mapping(conn, "beta.City", "city_name", "city_id")

    # Load Botanists
    logging.info("Loading botanists")
    for _, row in data.iterrows():
        insert_db(
            conn,
            """
            INSERT INTO beta.Botanist (first_name, last_name, email, phone_number)
            VALUES (?, ?, ?, ?)
            """,
            (
                row["first_name"],
                row["last_name"],
                row["email"],
                row["phone_cleaned"],
            ),
        )

    botanist_map = get_mapping(conn, "beta.Botanist", "email", "botanist_id")

    # Load Plants
    logging.info("Loading plants")
    for _, row in data.iterrows():
        insert_db(
            conn,
            """
            INSERT INTO beta.Plant (plant_name, scientific_name, last_watered, city_id)
            VALUES (?, ?, ?, ?)
            """,
            (
                row["name"],
                row["scientific_name"],
                row["last_watered"],
                city_map[row["origin_location"]["city"]],
            ),
        )

    plant_map = get_mapping(conn, "beta.Plant", "plant_name", "plant_id")

    # Load Readings
    logging.info("Loading readings")
    for _, row in data.iterrows():
        insert_db(
            conn,
            """
            INSERT INTO beta.Reading (temperature, soil_moisture, recording_taken, plant_id, botanist_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                row["temperature"],
                row["soil_moisture"],
                row["recording_taken"],
                plant_map[row["name"]],
                botanist_map[row["email"]],
            ),
        )

    conn.close()
    logging.info("Data load completed successfully.")


if __name__ == "__main__":
    load_data()
