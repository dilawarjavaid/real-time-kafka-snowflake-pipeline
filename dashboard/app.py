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
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

@st.cache_resource
def get_connection():

    try:
        account = st.secrets["SNOWFLAKE_ACCOUNT"]
        user = st.secrets["SNOWFLAKE_USER"]
        password = st.secrets["SNOWFLAKE_PASSWORD"]
        warehouse = st.secrets["SNOWFLAKE_WAREHOUSE"]
        database = st.secrets["SNOWFLAKE_DATABASE"]

    except Exception:
        account = os.getenv("SNOWFLAKE_ACCOUNT")
        user = os.getenv("SNOWFLAKE_USER")
        password = os.getenv("SNOWFLAKE_PASSWORD")
        warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
        database = os.getenv("SNOWFLAKE_DATABASE")

    return snowflake.connector.connect(
        account=account,
        user=user,
        password=password,
        warehouse=warehouse,
        database=database,
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

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "🌡️ Temperature",
        f"{latest['AVG_TEMPERATURE']:.1f} °C"
    )

    col2.metric(
        "💧 Humidity",
        f"{latest['AVG_HUMIDITY']:.1f}%"
    )

    col3.metric(
        "💨 Wind Speed",
        f"{latest['AVG_WIND_SPEED']:.1f} km/h"
    )

    col4.metric(
        "📊 Readings",
        f"{int(latest['READING_COUNT']):,}"
    )

    st.subheader("📈 Weather Trends")

    tab1, tab2, tab3 = st.tabs([
        "Temperature",
        "Humidity",
        "Wind Speed"
    ])

    with tab1:
        st.line_chart(
            df,
            x="WEATHER_HOUR",
            y="AVG_TEMPERATURE"
        )

    with tab2:
        st.line_chart(
            df,
            x="WEATHER_HOUR",
            y="AVG_HUMIDITY"
        )

    with tab3:
        st.line_chart(
            df,
            x="WEATHER_HOUR",
            y="AVG_WIND_SPEED"
        )

    st.subheader("⚙️ Pipeline Overview")

    st.info(
        "Open-Meteo API → Python Producer → Apache Kafka → "
        "Snowflake Bronze → Stream + Task → Silver → Gold → Streamlit"
    )

    st.subheader("Hourly Weather Data")

    st.dataframe(
        df.sort_values("WEATHER_HOUR", ascending=False),
        use_container_width=True
    )