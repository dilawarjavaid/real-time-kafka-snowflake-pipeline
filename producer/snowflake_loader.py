import json
import os

import snowflake.connector
from dotenv import load_dotenv

load_dotenv()


def insert_weather_data(weather_data):

    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )

    try:
        cursor = conn.cursor()

        query = """
        INSERT INTO WEATHER_RAW (RAW_DATA)
        SELECT PARSE_JSON(%s)
        """

        cursor.execute(
            query,
            (json.dumps(weather_data),)
        )

        conn.commit()

        print("Inserted into Snowflake")

    finally:
        cursor.close()
        conn.close()