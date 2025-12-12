#!/bin/bash

# Start script for Backend Services
# Run this on your laptop to start the classifier service and API server

echo "========================================="
echo "Fruit Classification System - Backend"
echo "========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Start RabbitMQ
echo ""
echo "Starting RabbitMQ..."
docker-compose up -d

# Wait for RabbitMQ to be ready
echo "Waiting for RabbitMQ to be ready..."
sleep 5

# Check if RabbitMQ is running
if docker ps | grep -q fruit_rabbitmq; then
    echo "✅ RabbitMQ is running"
    echo "   Management UI: http://localhost:15672 (guest/guest)"
else
    echo "❌ RabbitMQ failed to start"
    exit 1
fi

# Create virtual environment if it doesn't exist
cd backend
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your configuration"
fi

# Create directories
mkdir -p models data

echo ""
echo "========================================="
echo "Starting Backend Services..."
echo "========================================="

# Start classifier service in background
echo ""
echo "Starting Classifier Service..."
python classifier_service.py &
CLASSIFIER_PID=$!
echo "✅ Classifier Service started (PID: $CLASSIFIER_PID)"

# Wait a bit
sleep 2

# Start API server
echo ""
echo "Starting API Server..."
python api.py &
API_PID=$!
echo "✅ API Server started (PID: $API_PID)"

echo ""
echo "========================================="
echo "Backend Services Running!"
echo "========================================="
echo "API Server: http://localhost:8000"
echo "Dashboard: http://localhost:8000/dashboard/"
echo "RabbitMQ Management: http://localhost:15672"
echo ""
echo "Press Ctrl+C to stop all services"
echo "========================================="

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping services...'; kill $CLASSIFIER_PID $API_PID; docker-compose down; exit" INT
wait
