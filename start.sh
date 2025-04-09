#!/bin/bash

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    echo "No .env file found. Creating from .env.example"
    cp .env.example .env
    echo "Please edit .env file with your API keys and settings"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install Docker and Docker Compose first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

# Build and start the containers
echo "Starting WhatsApp Bot services..."
docker-compose up --build -d

# Check if services are running
echo "Checking service status..."
sleep 5
if [ "$(docker ps -q -f name=whatsapp-bot-server)" ] && [ "$(docker ps -q -f name=whatsapp-bot-connector)" ]; then
    echo "✅ WhatsApp Bot is running!"
    echo "WebSocket server available at: ws://localhost:8765"
    echo "Twilio connector available at: http://localhost:4000/webhook"
    echo "To expose your webhook publicly, use ngrok: ngrok http 4000"
else
    echo "❌ There was a problem starting the services. Check the logs with:"
    echo "docker-compose logs"
fi
