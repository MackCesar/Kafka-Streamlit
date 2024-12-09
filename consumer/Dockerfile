FROM python:3.9-slim
WORKDIR /app
COPY weather_consumer.py .
RUN pip install kafka-python pandas
CMD ["python", "weather_consumer.py"]