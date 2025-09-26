import altair as alt


def plot_temp_vs_moisture(df):
    """Scatter plot of temperature vs soil moisture."""
    return (
        alt.Chart(df)
        .mark_circle(size=60, color="green", opacity=0.6)
        .encode(
            x=alt.X("average_temperature:Q", title="Average Temperature (°C)"),
            y=alt.Y("average_soil_moisture:Q",
                    title="Average Soil Moisture (%)"),
            tooltip=["plant_id", "average_temperature",
                     "average_soil_moisture", "timestamp"]
        )
        .interactive()
    )
# Works


def plot_time_series(df, y_col, title):
    """Line plot of time series."""
    return (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("timestamp:T", title="Time"),
            y=alt.Y(f"{y_col}:Q", title=title),
            tooltip=["plant_id", "timestamp", y_col]
        )
        .properties(title=title)
        .interactive()
    )
