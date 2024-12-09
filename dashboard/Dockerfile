# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy application files
COPY weather_dashboard.py /app/
COPY ../requirements.txt /app/
COPY .env .

# Install dependencies
RUN pip install streamlit kafka-python>=2.0 requests pandas python-dotenv streamlit-autorefresh streamlit-javascript

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "weather_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]