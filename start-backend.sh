#!/bin/bash
# Start Backend Services (Linux/Mac)

echo "========================================"
echo "Starting Backend Services"
echo "========================================"
echo ""

# Check if RabbitMQ is running
echo "[1/3] Checking RabbitMQ status..."
if systemctl is-active --quiet rabbitmq-server 2>/dev/null; then
    echo "RabbitMQ is running"
elif brew services list | grep rabbitmq | grep started >/dev/null 2>&1; then
    echo "RabbitMQ is running"
else
    echo "RabbitMQ is not running. Starting..."
    # Try systemctl (Linux)
    sudo systemctl start rabbitmq-server 2>/dev/null || \
    # Try brew (Mac)
    brew services start rabbitmq 2>/dev/null
    sleep 3
fi

echo ""
echo "[2/3] Starting Classifier Service..."
echo "Running in background..."
python classifier_service.py &
CLASSIFIER_PID=$!

# Wait a bit
sleep 2

echo ""
echo "[3/3] Starting API Server..."
echo "Press Ctrl+C to stop"
echo ""

# Start API (will run in foreground)
python api.py

# Cleanup on exit
kill $CLASSIFIER_PID 2>/dev/null
