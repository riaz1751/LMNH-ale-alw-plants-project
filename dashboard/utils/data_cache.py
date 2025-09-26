import streamlit as st
import pandas as pd
import awswrangler as wr
from .db_utils import get_connection


@st.cache_data(ttl=600)  # cache for 10 min
def get_summary_data() -> pd.DataFrame:
    query = """
    SELECT plant_id, average_temperature, average_soil_moisture,
           year, month, day, hour
    FROM summary
    """
    df = wr.athena.read_sql_query(
        sql=query,
        database="c19-cran-plants-db",
        ctas_approach=False
    )

    # Combine into proper timestamp
    df["timestamp"] = pd.to_datetime(
        df["year"].astype(str)
        + "-" + df["month"].astype(str)
        + "-" + df["day"].astype(str)
        + " " + df["hour"].astype(str) + ":00:00",
        errors="coerce"
    )

    return df


def query_db(query: str) -> pd.DataFrame:
    """Run a query and return results as DataFrame."""
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data(ttl=300)
def get_live_data():
    """Fetch the latest readings from RDS with standardized column names."""

    query = """
        SELECT r.reading_id,
               r.temperature,
               r.soil_moisture,
               r.recording_taken,
               p.plant_id,
               p.plant_name,
               c.city_name,
               co.country_name
        FROM beta.Reading r
        JOIN beta.Plant p ON r.plant_id = p.plant_id
        JOIN beta.City c ON p.city_id = c.city_id
        JOIN beta.Country co ON c.country_id = co.country_id;
    """

    df = query_db(query)

    # Standardize time column
    df = df.rename(columns={"recording_taken": "timestamp"})
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    return df
