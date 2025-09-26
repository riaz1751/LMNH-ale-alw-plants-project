import streamlit as st
import pandas as pd
from utils.data_cache import get_summary_data
from utils.charts import plot_temp_vs_moisture, plot_time_series
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Plant Dashboard", layout="wide")

st.title("Plant Monitoring Dashboard")

# Load summary data from Athena
summary = get_summary_data()

# Reconstruct timestamp column
summary["timestamp"] = pd.to_datetime(
    summary["year"].astype(str) + "-" +
    summary["month"].astype(str) + "-" +
    summary["day"].astype(str) + " " +
    summary["hour"].astype(str) + ":00:00",
    errors="coerce"
)

# Sidebar filters
st.sidebar.header("Filters")

plants = summary["plant_id"].unique().tolist()
selected_plants = st.sidebar.multiselect(
    "Select Plant(s)", plants, default=plants)

min_date, max_date = summary["timestamp"].min(), summary["timestamp"].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# Apply filters
filtered = summary[summary["plant_id"].isin(selected_plants)]
filtered = filtered[
    (filtered["timestamp"].dt.date >= date_range[0]) &
    (filtered["timestamp"].dt.date <= date_range[1])
]

# Charts
st.subheader("Temperature vs Soil Moisture")
st.altair_chart(plot_temp_vs_moisture(filtered), use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Temperature Over Time")
    st.altair_chart(plot_time_series(filtered, "average_temperature", "Temperature Over Time"),
                    use_container_width=True)

with col2:
    st.subheader("Soil Moisture Over Time")
    st.altair_chart(plot_time_series(filtered, "average_soil_moisture", "Soil Moisture Over Time"),
                    use_container_width=True)
