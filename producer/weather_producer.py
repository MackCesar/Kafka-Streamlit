from kafka import KafkaProducer
import json
import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Kafka Configuration
KAFKA_BROKER = os.getenv("KAFKA_BROKER")
KAFKA_TOPIC = "weather-raw"

# API Configuration
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

# Path to cities.json
CITIES_FILE = "./cities.json"

# Kafka Producer Initialization
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    api_version=(2, 7, 0)  # Adjust to match your Kafka broker version
)

# Function to load cities dynamically
def load_cities():
    if os.path.exists(CITIES_FILE):
        try:
            with open(CITIES_FILE, "r") as file:
                cities = json.load(file)
                if isinstance(cities, list) and cities:
                    return cities
        except json.JSONDecodeError as e:
            print(f"❌ Error in cities.json format: {e}")
    print("⚠️ Falling back to default cities.")
    return ["New York", "Los Angeles", "Chicago", "Houston", "San Francisco"]

# Function to fetch weather data
def fetch_weather(city):
    params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
    response = requests.get(WEATHER_API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    print(f"⚠️ Failed to fetch data for {city}: {response.text}")
    return None

def on_send_success(record_metadata):
    print(f"✅ Sent: {record_metadata.topic} - Partition: {record_metadata.partition}")

def on_send_error(excp):
    print(f"❌ Error while sending: {excp}")

if __name__ == "__main__":
    print("🚀 Starting Weather Producer...")
    while True:
        cities = load_cities()  # Dynamically load cities
        for city in cities:
            weather_data = fetch_weather(city)
            if weather_data:
                message = {
                    "City": weather_data.get("name"),
                    "Temperature": weather_data["main"].get("temp"),
                    "Humidity": weather_data["main"].get("humidity"),
                    "Condition": weather_data["weather"][0]["description"],
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                producer.send(KAFKA_TOPIC, value=message).add_callback(on_send_success).add_errback(on_send_error)
        print("⏳ Waiting before fetching data again...")
        time.sleep(10)  # Fetch data every 10 seconds