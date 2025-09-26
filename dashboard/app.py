import streamlit as st
from data_cache import get_summary_data, get_live_data
from charts import plot_temp_vs_moisture, plot_time_series
from dotenv import load_dotenv

load_dotenv()
st.title("Plant Monitoring Dashboard")

# Choose data source
data_source = st.sidebar.radio(
    "Select Data Source:",
    ("Summary (S3/Athena)", "Live (RDS)")
)


if data_source == "Summary (S3/Athena)":
    df = get_summary_data()

    plant_options = df["plant_id"].dropna().unique().tolist()
    selected_plant = st.sidebar.selectbox("Select Plant ID", plant_options)
    filtered = df[df["plant_id"] == selected_plant]
else:
    df = get_live_data()
    # Filters
    plant_options = df["plant_name"].dropna().unique().tolist()
    selected_plant = st.sidebar.selectbox("Select Plant", plant_options)

    if selected_plant:
        filtered = df[df["plant_name"] == selected_plant]
    else:
        filtered = df

# Charts
if data_source == "Summary (S3/Athena)":
    st.altair_chart(
        plot_temp_vs_moisture(filtered),
        use_container_width=True
    )
    st.altair_chart(
        plot_time_series(filtered, "average_temperature",
                         "Temperature Over Time"),
        use_container_width=True
    )
    st.altair_chart(
        plot_time_series(filtered, "average_soil_moisture",
                         "Soil Moisture Over Time"),
        use_container_width=True
    )
else:
    st.altair_chart(
        plot_time_series(filtered, "temperature",
                         "Live Temperature Over Time"),
        use_container_width=True
    )
    st.altair_chart(
        plot_time_series(filtered, "soil_moisture",
                         "Live Soil Moisture Over Time"),
        use_container_width=True
    )
