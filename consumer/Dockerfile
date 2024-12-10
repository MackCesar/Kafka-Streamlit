FROM python:3.9-slim
WORKDIR /app
COPY weather_consumer.py .
#RUN pip install kafka-python pandas
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "weather_consumer.py"]