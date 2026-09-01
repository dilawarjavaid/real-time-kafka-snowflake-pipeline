import json
from snowflake_loader import insert_weather_data
from kafka import KafkaConsumer


consumer = KafkaConsumer(
    "weather-topic",
    bootstrap_servers="localhost:9092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="weather-consumer-group",
    value_deserializer=lambda value: json.loads(value.decode("utf-8"))
)


print("Waiting for weather data...")


for message in consumer:

    weather = message.value

    print(
        f"Temperature: {weather['temperature']}°C | "
        f"Humidity: {weather['humidity']}% | "
        f"Wind: {weather['wind_speed']} km/h"
    )

    insert_weather_data(weather)