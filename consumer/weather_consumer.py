from kafka import KafkaConsumer
import json
import logging
import os

# Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants and Defaults
CITIES_FILE = "./cities.json"  # Path to cities.json
DEFAULT_CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "San Francisco"]

# Kafka Configuration
KAFKA_TOPIC = "weather-raw"
KAFKA_BROKER = os.getenv("KAFKA_BROKER")  # Default to localhost if not set

# Function to Load Cities Dynamically
def load_cities():
    try:
        if os.path.exists(CITIES_FILE):
            with open(CITIES_FILE, "r") as file:
                cities = json.load(file)
                if isinstance(cities, list) and cities:  # Ensure it's a non-empty list
                    return cities
                else:
                    logging.warning("⚠️ cities.json is empty or invalid. Using default cities.")
        return DEFAULT_CITIES
    except Exception as e:
        logging.error(f"❌ Error loading cities.json: {e}")
        return DEFAULT_CITIES

# Function to Initialize Kafka Consumer
def get_kafka_consumer():
    try:
        logging.info(f"🔍 Connecting to Kafka broker at: {KAFKA_BROKER}")
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            auto_offset_reset="latest",
            enable_auto_commit=True,
            group_id="dashboard-group-unique",
            api_version=(2, 5, 0),  # Explicit Kafka API version
        )
        logging.info("✅ Successfully connected to Kafka.")
        return consumer
    except Exception as e:
        logging.error(f"❌ Failed to connect to Kafka: {e}")
        return None

# Function to Process Weather Data
def process_weather_data(data, cities):
    city = data.get("City", "Unknown")
    if city in cities:
        temp = data.get("Temperature", "N/A")
        condition = data.get("Condition", "N/A")
        timestamp = data.get("Timestamp", "N/A")
        logging.info(f"✅ {city} -> Temperature: {temp}°C, Condition: {condition}, Time: {timestamp}")
    else:
        logging.info(f"🚫 {city} is not in the selected cities list. Ignoring.")

# Main Consumer Loop
if __name__ == "__main__":
    cities = load_cities()
    consumer = get_kafka_consumer()

    if consumer:
        logging.info("📡 Kafka Weather Consumer started... Listening for messages.")
        try:
            while True:
                for message in consumer:
                    data = message.value
                    process_weather_data(data, cities)
                cities = load_cities()  # Reload cities dynamically on each iteration
        except KeyboardInterrupt:
            logging.info("🛑 Consumer stopped.")
        finally:
            consumer.close()
            logging.info("✅ Kafka Consumer closed.")
    else:
        logging.error("❌ Unable to initialize Kafka Consumer. Check your configuration.")