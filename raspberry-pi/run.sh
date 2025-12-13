#!/bin/bash
# Start Raspberry Pi Control Server and Main Application

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "  Raspberry Pi Fruit Sorting System"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo -e "${YELLOW}Run setup first: ./start.sh${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}✅ Activating virtual environment...${NC}"
source venv/bin/activate

# Check Python packages availability
echo -e "${GREEN}Checking Python packages...${NC}"
python3 -c "
try:
    import RPi.GPIO, pika, cv2, PIL
    print('✅ Core packages available')
    
    # Check camera libraries
    camera_available = False
    try:
        import picamera2
        print('✅ picamera2 available (Raspberry Pi Camera)')
        camera_available = True
    except ImportError:
        print('⚠️  picamera2 not available')
    
    if not camera_available:
        try:
            import cv2
            print('✅ OpenCV available (USB/fallback camera)')
            camera_available = True
        except ImportError:
            pass
    
    if not camera_available:
        print('❌ No camera library available')
        print('Install: pip install picamera2 OR ensure OpenCV works')
        exit(1)
        
except ImportError as e:
    print(f'❌ Missing package: {e}')
    print('Run: ./start.sh to install missing packages')
    exit(1)
"
if [ $? -ne 0 ]; then
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    echo "✅ Loading .env configuration..."
    export $(grep -v '^#' .env | xargs)
fi

# Test RabbitMQ connection
echo ""
echo "Testing RabbitMQ connection to ${RABBITMQ_HOST:-100.112.253.55}..."
python3 -c "
import pika
import sys
try:
    credentials = pika.PlainCredentials('${RABBITMQ_USER:-guest}', '${RABBITMQ_PASSWORD:-guest}')
    params = pika.ConnectionParameters(
        host='${RABBITMQ_HOST:-100.112.253.55}',
        port=${RABBITMQ_PORT:-5672},
        credentials=credentials,
        connection_attempts=2,
        socket_timeout=5
    )
    conn = pika.BlockingConnection(params)
    conn.close()
    print('✅ RabbitMQ connection OK!')
except Exception as e:
    print(f'⚠️  RabbitMQ not available: {e}')
    print('   Make sure RabbitMQ is running on laptop!')
"

# Cleanup function
cleanup() {
    echo ""
    echo "Shutting down..."
    if [ ! -z "$CONTROL_PID" ]; then
        kill $CONTROL_PID 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Start control server in background
echo ""
echo "Starting hardware control server on port 5000..."
python3 control_server.py &
CONTROL_PID=$!

# Wait for control server to start
sleep 2

# Start main application
echo ""
echo "Starting main classification system..."
echo "Press Ctrl+C to stop"
echo ""
python3 main.py