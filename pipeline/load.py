"""Loading the transformed data into the RDS database."""
import logging
from connect_db_utils import get_connection, insert_db, get_mapping
from transform import clean_valid_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def load_data():
    """Load transformed plant data into SQL Server RDS, enforcing uniqueness for
    country, city, botanist, and plant."""
    conn = get_connection()

    # Get cleaned & transformed dataframe
    df = clean_valid_data()

    # Load Countries
    logging.info("Loading countries")
    country_map = get_mapping(conn, "beta.Country",
                              "country_name", "country_id")
    for country in df["origin_location"].apply(lambda x: x.get("country")).unique():
        if country not in country_map:
            insert_db(
                conn, "INSERT INTO beta.Country (country_name) VALUES (?)", (country,))
    country_map = get_mapping(conn, "beta.Country",
                              "country_name", "country_id")

    # Load Cities
    logging.info("Loading cities")
    # For uniqueness, combine city_name + country_id
    city_map = {}
    with conn.cursor() as cur:
        cur.execute("SELECT city_id, city_name, country_id FROM beta.City;")
        for city_id, city_name, country_id in cur.fetchall():
            city_map[(city_name, country_id)] = city_id

    for _, row in df.iterrows():
        city = row["origin_location"]["city"]
        country = row["origin_location"]["country"]
        country_id = country_map[country]

        if (city, country_id) not in city_map:
            insert_db(
                conn,
                "INSERT INTO beta.City (city_name, lat, long, country_id) VALUES (?, ?, ?, ?)",
                (city, row["origin_location"]["latitude"],
                 row["origin_location"]["longitude"], country_id),
            )
    # Refresh mapping
    city_map = {}
    with conn.cursor() as cur:
        cur.execute("SELECT city_id, city_name, country_id FROM beta.City;")
        for city_id, city_name, country_id in cur.fetchall():
            city_map[(city_name, country_id)] = city_id

    # Load Botanists
    logging.info("Loading botanists...")
    botanist_map = get_mapping(conn, "beta.Botanist", "email", "botanist_id")
    for _, row in df.iterrows():
        email = row["email"]
        if email not in botanist_map:
            insert_db(
                conn,
                "INSERT INTO beta.Botanist (first_name, last_name, email, phone_number) VALUES (?, ?, ?, ?)",
                (row["first_name"], row["last_name"],
                 row["email"], row["phone_valid"]),
            )
    botanist_map = get_mapping(conn, "beta.Botanist", "email", "botanist_id")

    # Load Plants
    logging.info("Loading plants")
    # For uniqueness, combine plant_name + city_id
    plant_map = {}
    with conn.cursor() as cur:
        cur.execute("SELECT plant_id, plant_name, city_id FROM beta.Plant;")
        for plant_id, plant_name, city_id in cur.fetchall():
            plant_map[(plant_name, city_id)] = plant_id

    for _, row in df.iterrows():
        city_id = city_map[(row["origin_location"]["city"],
                            country_map[row["origin_location"]["country"]])]
        if (row["name"], city_id) not in plant_map:
            insert_db(
                conn,
                "INSERT INTO beta.Plant (plant_name, scientific_name, last_watered, city_id) VALUES (?, ?, ?, ?)",
                (row["name"], ",".join(row["scientific_name"]),
                 row["last_watered"], city_id),
            )
    # Refresh plant mapping
    plant_map = {}
    with conn.cursor() as cur:
        cur.execute("SELECT plant_id, plant_name, city_id FROM beta.Plant;")
        for plant_id, plant_name, city_id in cur.fetchall():
            plant_map[(plant_name, city_id)] = plant_id

    # Load Readings
    logging.info("Loading readings")
    for _, row in df.iterrows():
        city_id = city_map[(row["origin_location"]["city"],
                            country_map[row["origin_location"]["country"]])]
        plant_id = plant_map[(row["name"], city_id)]
        botanist_id = botanist_map[row["email"]]
        insert_db(
            conn,
            "INSERT INTO beta.Reading (temperature, soil_moisture, recording_taken, plant_id, botanist_id) VALUES (?, ?, ?, ?, ?)",
            (row["temperature"], row["soil_moisture"],
             row["recording_taken"], plant_id, botanist_id),
        )

    logging.info("Data load complete.")
    conn.close()


if __name__ == "__main__":
    load_data()
