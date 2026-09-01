import os

import pandas as pd
import snowflake.connector
import streamlit as st
from dotenv import load_dotenv


load_dotenv()


st.set_page_config(
    page_title="Real-Time Weather Pipeline",
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ Real-Time Weather Analytics")
st.caption("Kafka → Snowflake → Streamlit")


@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema="GOLD"
    )


@st.cache_data(ttl=30)
def load_weather_data():
    conn = get_connection()

    query = """
        SELECT
            WEATHER_HOUR,
            AVG_TEMPERATURE,
            MIN_TEMPERATURE,
            MAX_TEMPERATURE,
            AVG_HUMIDITY,
            AVG_WIND_SPEED,
            READING_COUNT
        FROM REAL_TIME_PIPELINE.GOLD.HOURLY_WEATHER
        ORDER BY WEATHER_HOUR
    """

    return pd.read_sql(query, conn)


df = load_weather_data()


if df.empty:
    st.warning("No weather data available.")
else:
    latest = df.iloc[-1]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Temperature",
        f"{latest['AVG_TEMPERATURE']} °C"
    )

    col2.metric(
        "Average Humidity",
        f"{latest['AVG_HUMIDITY']} %"
    )

    col3.metric(
        "Average Wind Speed",
        f"{latest['AVG_WIND_SPEED']} km/h"
    )

    st.subheader("Temperature Over Time")

    st.line_chart(
        df,
        x="WEATHER_HOUR",
        y="AVG_TEMPERATURE"
    )

    st.subheader("Hourly Weather Data")

    st.dataframe(
        df.sort_values("WEATHER_HOUR", ascending=False),
        use_container_width=True
    )