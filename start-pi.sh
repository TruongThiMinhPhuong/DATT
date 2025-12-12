#!/bin/bash

# Start script for Raspberry Pi
# Run this on your Raspberry Pi to start the fruit sorting system

echo "========================================="
echo "Fruit Classification System - Raspberry Pi"
echo "========================================="

# Check for root/sudo
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Please do NOT run as root/sudo"
    exit 1
fi

# Navigate to script directory
cd "$(dirname "$0")/raspberry-pi"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    echo "Creating from template..."
    cp .env.example .env
    echo "⚠️  Please edit raspberry-pi/.env with your laptop's IP address"
    echo "   Set RABBITMQ_HOST=<your_laptop_ip>"
    exit 1
fi

# Create virtual environment if needed
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Check camera
echo ""
echo "Checking camera..."
vcgencmd get_camera 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Cannot check camera status"
    echo "   Make sure camera is enabled in raspi-config"
fi

# Test imports
echo ""
echo "Verifying imports..."
python3 << EOF
try:
    import picamera2
    import RPi.GPIO as GPIO
    import pika
    print("✅ All imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "❌ Import verification failed"
    exit 1
fi

echo ""
echo "========================================="
echo "Starting Fruit Sorting System..."
echo "========================================="
echo ""

# Run main application
python main.py

# Cleanup on exit
echo ""
echo "Cleaning up GPIO..."
python3 << EOF
import RPi.GPIO as GPIO
GPIO.cleanup()
EOF

echo "Shutdown complete."
