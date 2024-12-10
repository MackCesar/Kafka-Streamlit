FROM python:3.9

WORKDIR /app
COPY weather_producer.py .
COPY requirements.txt .
COPY .env .

# Install dependencies
RUN pip install --no-cache-dir kafka-python>=2.0 requests pandas python-dotenv
#RUN pip install --upgrade pip
#RUN pip install --no-cache-dir -r requirements.txt

# Run the Python script


CMD ["python", "weather_producer.py"]