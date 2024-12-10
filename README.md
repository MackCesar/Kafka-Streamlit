# Real-Time Weather Dashboard

A real-time weather dashboard built with **Streamlit**, **Kafka**, and **OpenWeather API**. The app streams live weather updates from a Kafka topic, displays them in a scrollable, dynamically resized table, and allows users to select which cities to track. The table refreshes at a user-defined interval, and data is persisted between refreshes to ensure a stable viewing experience.

## Features

- **Dynamic City Selection:** Choose which cities to monitor from a predefined list.
- **Adjustable Refresh Rate:** Control how frequently the dashboard fetches new data from Kafka.
- **Dynamic Table Height:** The table automatically sizes based on the user's screen height, ensuring a comfortable viewing experience without going off-screen.
- **Persistent Data:** Previously fetched weather updates remain visible even when no new data arrives.
- **Secure Configuration:** Sensitive API keys and configuration details are stored in a local `.env` file, never committed to version control.

## Requirements

- **Python 3.9+**
- **Kafka** running locally or accessible remotely.
- **OpenWeather API Key** (placed in `.env` file)
- **Poetry or pip** to install dependencies.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/MackCesar/Kafka-Streamlit.git
   cd weather-dashboard 
   ```
   
2. Create a .env file with your API key:
    ```bash 
    echo "WEATHER_API_KEY=your_api_key_here" > .env
    ```
3.	Install the required Python packages:
    ```bash 
    pip install -r requirements.txt
    ```
    (If you don’t have a requirements.txt, use pip freeze > requirements.txt after installing your deps. Ensure that streamlit, kafka-python, streamlit-autorefresh, and streamlit-javascript are included.)

4. 	Run the Streamlit app:
     ``` 
    docker-compose up --build
    ```
5. Open http://localhost:8501 in your browser to view the dashboard.

### Contributing

Contributions are welcome! Feel free to open issues or submit PRs for enhancements.

### License

This project is available under the MIT License. See LICENSE for details.
