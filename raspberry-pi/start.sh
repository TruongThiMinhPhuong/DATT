#!/bin/bash
echo "=========================================="
echo "🍓 AI Fruit Sorting System - Installation"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo -e "${YELLOW}⚠️  Warning: This script is designed for Raspberry Pi${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

cd "$(dirname "$0")"

echo ""
echo "Step 1: Setting up swap space (4GB)..."
echo "💡 This is CRITICAL for training AI models on Pi!"

# Check current swap
current_swap=$(free -m | awk '/Swap:/ {print $2}')
if [ "$current_swap" -lt 4000 ]; then
    echo "   Current swap: ${current_swap}MB, increasing to 4GB..."
    
    sudo dphys-swapfile swapoff
    sudo sed -i 's/^CONF_SWAPSIZE=.*/CONF_SWAPSIZE=4096/' /etc/dphys-swapfile
    sudo dphys-swapfile setup
    sudo dphys-swapfile swapon
    
    new_swap=$(free -m | awk '/Swap:/ {print $2}')
    echo -e "${GREEN}   ✓ Swap increased to ${new_swap}MB${NC}"
else
    echo -e "${GREEN}   ✓ Swap already configured (${current_swap}MB)${NC}"
fi

echo ""
echo "Step 2: Updating system packages..."
sudo apt update
sudo apt upgrade -y

echo ""
echo "Step 3: Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    libopencv-dev \
    python3-opencv \
    libatlas-base-dev \
    libcap-dev \
    libffi-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    cmake

echo ""
echo "Step 4: Installing camera system packages..."
sudo apt install -y \
    libcamera-dev \
    libcamera-apps \
    python3-libcamera \
    python3-kms++ \
    python3-picamera2 \
    python3-prctl

echo ""
echo "Step 5: Enabling camera and GPIO..."
sudo raspi-config nonint do_camera 0
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0

echo ""
echo "Step 6: Creating virtual environment..."
if [ ! -d "venv" ]; then
    # Create venv WITH system-site-packages for libcamera/picamera2 access
    python3 -m venv --system-site-packages venv
    echo -e "${GREEN}   ✓ Virtual environment created with system-site-packages${NC}"
else
    echo "   Virtual environment already exists"
fi

source venv/bin/activate

echo ""
echo "Step 7: Upgrading pip..."
pip install --upgrade pip setuptools wheel

echo ""
echo "Step 8: Installing Python packages..."
echo "   Installing packages individually to skip problematic ones..."

# Core packages
echo "   📦 Core packages..."
pip install numpy pillow pyyaml loguru || echo "   ⚠️  Some core packages failed"

# OpenCV
echo "   📦 OpenCV..."
pip install opencv-python || echo "   ⚠️  OpenCV failed"

# AI Models
echo "   📦 AI packages..."
pip install ultralytics || echo "   ⚠️  Ultralytics failed"

# TensorFlow Lite
echo "   📦 TensorFlow Lite..."
pip install tflite-runtime || pip install tensorflow==2.13.0 || echo "   ⚠️  TFLite failed"

# Hardware packages
echo "   📦 Hardware packages..."
pip install RPi.GPIO gpiozero || echo "   ⚠️  GPIO packages failed"

# Picamera2 - Try pip first, then link system package
echo "   📦 Picamera2..."
pip install picamera2 2>/dev/null || {
    echo "      ℹ️  pip install failed, linking system package..."
    PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    mkdir -p venv/lib/python${PYTHON_VER}/site-packages/
    ln -sf /usr/lib/python3/dist-packages/picamera2 venv/lib/python${PYTHON_VER}/site-packages/ 2>/dev/null
    ln -sf /usr/lib/python3/dist-packages/libcamera venv/lib/python${PYTHON_VER}/site-packages/ 2>/dev/null
}

echo ""
echo -e "${GREEN}=========================================="
echo -e "✅ Installation completed!"
echo -e "=========================================="${NC}
echo ""
echo "📋 Next steps:"
echo "   1. Reboot your Raspberry Pi: sudo reboot"
echo "   2. Test camera: libcamera-hello"
echo "   3. Run the system: ./run.sh"
echo ""
