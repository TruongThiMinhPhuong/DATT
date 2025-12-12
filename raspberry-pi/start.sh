#!/bin/bash
# Start Raspberry Pi Control Server and Main Application

echo "Starting Raspberry Pi Fruit Sorting System..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start control server in background
echo "Starting hardware control server on port 5000..."
python3 control_server.py &
CONTROL_PID=$!

# Wait a bit for control server to start
sleep 2

# Start main application
echo "Starting main classification system..."
python3 main.py

# Cleanup on exit
trap "kill $CONTROL_PID" EXIT
