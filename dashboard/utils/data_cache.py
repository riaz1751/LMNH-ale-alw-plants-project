from os import environ as ENV
import streamlit as st
import awswrangler as wr
import pandas as pd
from .db_utils import get_connection, query_db, boto3_session


@st.cache_data
def get_summary_data() -> pd.DataFrame:
    """Fetch summary data from Athena."""
    query = """
        SELECT *
        FROM summary
    """
    df = wr.athena.read_sql_query(
        sql=query,
        database=ENV["ATHENA_DB"],
        boto3_session=boto3_session()
    )
    return df


@st.cache_data
def get_plants() -> list[tuple[int, str]]:
    """Fetch plant_id and plant_name from RDS."""
    conn = get_connection()
    rows = query_db(conn, "SELECT plant_id, plant_name FROM beta.Plant;")
    conn.close()
    return rows


@st.cache_data
def get_cities() -> list[tuple[int, str]]:
    """Fetch city_id and city_name from RDS."""
    conn = get_connection()
    rows = query_db(conn, "SELECT city_id, city_name FROM beta.City;")
    conn.close()
    return rows


@st.cache_data
def get_countries() -> list[tuple[int, str]]:
    """Fetch country_id and country_name from RDS."""
    conn = get_connection()
    rows = query_db(conn, "SELECT country_id, country_name FROM beta.Country;")
    conn.close()
    return rows
