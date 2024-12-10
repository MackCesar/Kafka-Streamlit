import streamlit as st
from kafka import KafkaConsumer
import json
import pandas as pd
import os
from dotenv import load_dotenv
import logging
from streamlit_autorefresh import st_autorefresh
from streamlit_javascript import st_javascript

# Load environment variables
load_dotenv()

# Kafka Configuration
KAFKA_TOPIC = "weather-raw"
KAFKA_BROKER = os.getenv("KAFKA_BROKER")

# File Paths and Defaults
CITIES_FILE = "./cities.json"
DEFAULT_CITIES = ["New York", "Los Angeles", "Chicago", "Houston", "San Francisco", "Miami", "Orlando", "Tampa"]

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Streamlit Page Setup
st.set_page_config(page_title="Weather Dashboard", layout="wide")
st.title("🌍 Real-Time Weather Dashboard")

def load_cities():
    try:
        if os.path.exists(CITIES_FILE):
            with open(CITIES_FILE, "r") as file:
                cities = json.load(file)
                valid_cities = [c for c in cities if c in DEFAULT_CITIES]
                if valid_cities:
                    return valid_cities
                else:
                    st.warning("⚠️ No valid cities found in cities.json. Using default cities.")
        return DEFAULT_CITIES
    except Exception as e:
        st.error(f"❌ Error loading cities: {e}")
        return DEFAULT_CITIES

def save_cities(selected_cities):
    try:
        with open(CITIES_FILE, "w") as file:
            json.dump(selected_cities, file, indent=4)
        st.success("✅ City list updated successfully!")
        st.rerun()  # Reload to apply changes
    except Exception as e:
        st.error(f"❌ Failed to save cities: {e}")

@st.cache_resource
def get_consumer():
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BROKER,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            auto_offset_reset="latest",
            enable_auto_commit=True,
            group_id="dashboard-group-unique",
            api_version=(2, 5, 0),
        )
        st.success("✅ Successfully connected to Kafka.")
        return consumer
    except Exception as e:
        st.error(f"❌ Error initializing Kafka Consumer: {e}")
        return None

# Sidebar: City Selector
# Sidebar: City Selector, Refresh Rate, and now Temperature Unit Radio
st.sidebar.title("🌆 City Selector")
current_cities = load_cities()
current_cities = [c for c in current_cities if c in DEFAULT_CITIES] or DEFAULT_CITIES

selected_cities = st.sidebar.multiselect("Select Cities to Monitor", DEFAULT_CITIES, default=current_cities)
if st.sidebar.button("💾 Save Cities"):
    if selected_cities:
        save_cities(selected_cities)
    else:
        st.warning("⚠️ At least one city must be selected!")

refresh_rate = st.sidebar.slider("🔄 Refresh Rate (seconds)", 1, 10, 3)

# New Radio Button for Temperature Unit
temp_unit = st.sidebar.radio("Temperature Unit", ("C", "F"))

# Streaming State Control (unchanged)
if "streaming" not in st.session_state:
    st.session_state["streaming"] = False

if st.sidebar.button("🚀 Start Streaming"):
    st.session_state["streaming"] = True
    st.sidebar.success("✅ Streaming started!")

if st.sidebar.button("⏹️ Stop Streaming"):
    st.session_state["streaming"] = False
    st.sidebar.warning("🛑 Streaming stopped!")

consumer = get_consumer()

if "weather_df" not in st.session_state:
    st.session_state["weather_df"] = pd.DataFrame(
        columns=["City", "Temperature (°C)", "Humidity (%)", "Condition", "Timestamp"]
    )

def poll_kafka_messages():
    if consumer and st.session_state["streaming"]:
        cities = load_cities()
        new_data = []
        messages = consumer.poll(timeout_ms=1000)

        for _, records in messages.items():
            for record in records:
                data = record.value
                city = data.get("City", "Unknown")
                if city in cities:
                    # Store temperature in Celsius by default
                    new_data.append({
                        "City": city,
                        "Temperature (°C)": data.get("Temperature", "N/A"),  # Assume producer sends in Celsius
                        "Humidity (%)": data.get("Humidity", "N/A"),
                        "Condition": data.get("Condition", "N/A"),
                        "Timestamp": pd.Timestamp.now()
                    })

        if new_data:
            updated_df = pd.concat([st.session_state["weather_df"], pd.DataFrame(new_data)], ignore_index=True)
            updated_df.drop_duplicates(inplace=True)
            # Sort by Timestamp descending
            updated_df.sort_values(by="Timestamp", ascending=False, inplace=True)
            # Keep the most recent 50 entries
            updated_df = updated_df.head(50)
            st.session_state["weather_df"] = updated_df

poll_kafka_messages()

# Determine displayed DataFrame based on selected unit
display_df = st.session_state["weather_df"].copy()
display_df.reset_index(drop=True, inplace=True)

if not display_df.empty:
    if temp_unit == "F":
        # Convert Temperature (°C) to °F
        # Make sure temperature values are numeric before conversion
        # Non-numeric (e.g., "N/A") entries should be handled gracefully
        mask = pd.to_numeric(display_df["Temperature (°C)"], errors="coerce").notnull()
        display_df.loc[mask, "Temperature (°C)"] = (
            pd.to_numeric(display_df.loc[mask, "Temperature (°C)"]) * 9/5 + 32
        )
        # Rename column to Temperature (°F)
        display_df.rename(columns={"Temperature (°C)": "Temperature (°F)"}, inplace=True)

# Inject dynamic CSS for scrollable container (from previous code)
screen_height = st_javascript("window.innerHeight")
if screen_height is None:
    screen_height = 1100
else:
    try:
        screen_height = float(screen_height)
    except ValueError:
        screen_height = 1100
table_max_height = int(screen_height * 0.8)

st.markdown(f"""
<style>
.dataframe-container {{
    max-height: {table_max_height}px;
    overflow-y: auto;
}}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
st.dataframe(display_df, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state["streaming"]:
    st.info("🔴 Streaming is stopped. Click **Start Streaming** to begin.")
elif st.session_state["weather_df"].empty:
    # If never received data, table is empty but stable
    st.info("⏳ No new data yet. Waiting for updates...")

if not consumer:
    st.error("❌ Could not connect to Kafka. Check the Kafka broker configuration.")

if st.session_state["streaming"]:
    st_autorefresh(interval=refresh_rate * 1000, limit=None, key="autorefresh")

st.caption("Weather data powered by Kafka and OpenWeather API.")