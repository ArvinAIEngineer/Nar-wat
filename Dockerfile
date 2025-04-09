FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create start script for running both services
RUN echo '#!/bin/bash\n\
# Start Twilio connector in the background\n\
gunicorn --bind 0.0.0.0:4000 twilio_connector:app --daemon\n\
\n\
# Start WebSocket server in the foreground\n\
python whatsapp_bot.py\n' > /app/run.sh && chmod +x /app/run.sh

# Set environment variable for internal communication
ENV WEBSOCKET_URL=ws://localhost:8765

# Expose ports for Twilio webhook and WebSocket
EXPOSE 4000 8765

# Run the start script
CMD ["/app/run.sh"]
