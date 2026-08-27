import json
import time
import requests

from kafka import KafkaProducer


# Create Kafka producer
producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)


# Kafka topic
TOPIC = "weather-topic"


# Karachi coordinates
LATITUDE = 24.8607
LONGITUDE = 67.0011


def get_weather():

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m"
    }

    response = requests.get(url, params=params)

    response.raise_for_status()

    data = response.json()

    weather = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "temperature": data["current"]["temperature_2m"],
        "humidity": data["current"]["relative_humidity_2m"],
        "wind_speed": data["current"]["wind_speed_10m"],
        "timestamp": data["current"]["time"]
    }

    return weather


while True:

    weather_data = get_weather()

    print("Sending:", weather_data)

    producer.send(TOPIC, weather_data)

    producer.flush()

    time.sleep(10)