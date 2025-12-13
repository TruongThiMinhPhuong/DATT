#!/bin/bash
# Project Validation and Health Check Script
# Kiểm tra tình trạng toàn bộ dự án

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "="*60
echo -e "${BLUE}🔍 PROJECT HEALTH CHECK${NC}"
echo -e "${BLUE}🍓 Raspberry Pi Fruit Sorting System${NC}"
echo "="*60

# Check 1: Required Files
echo -e "\n${YELLOW}📁 Checking Required Files...${NC}"
required_files=(
    "config.py"
    "main.py" 
    "camera_module.py"
    "motor_controller.py"
    "rabbitmq_client.py"
    "control_server.py"
    "start.sh"
    "run.sh"
    "requirements.txt"
    ".env"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ✅ $file"
    else
        echo -e "   ❌ $file"
        missing_files+=("$file")
    fi
done

# Check 2: Virtual Environment
echo -e "\n${YELLOW}🐍 Checking Virtual Environment...${NC}"
if [ -d "venv" ]; then
    echo -e "   ✅ Virtual environment exists"
    if [ -f "venv/bin/activate" ]; then
        echo -e "   ✅ Activation script present"
    else
        echo -e "   ❌ Activation script missing"
    fi
else
    echo -e "   ❌ Virtual environment not found"
    echo -e "   ${YELLOW}Run: ./start.sh to create${NC}"
fi

# Check 3: Python Dependencies (if venv exists)
if [ -d "venv" ]; then
    echo -e "\n${YELLOW}📦 Checking Python Dependencies...${NC}"
    source venv/bin/activate
    
    # Core packages
    packages=("RPi.GPIO" "picamera2" "pika" "cv2" "PIL" "flask" "dotenv")
    
    for pkg in "${packages[@]}"; do
        if python3 -c "import $pkg" 2>/dev/null; then
            echo -e "   ✅ $pkg"
        else
            echo -e "   ❌ $pkg (missing)"
        fi
    done
fi

# Check 4: Configuration Files
echo -e "\n${YELLOW}⚙️  Checking Configuration...${NC}"
if [ -f ".env" ]; then
    echo -e "   ✅ .env file exists"
    if grep -q "RABBITMQ_HOST" .env; then
        echo -e "   ✅ RabbitMQ config present"
    else
        echo -e "   ⚠️  RabbitMQ config incomplete"
    fi
else
    echo -e "   ❌ .env file missing"
    if [ -f ".env.example" ]; then
        echo -e "   💡 Copy .env.example to .env and configure"
    fi
fi

# Check 5: Hardware Requirements
echo -e "\n${YELLOW}🔧 Hardware Requirements Check...${NC}"
echo -e "   📋 Required Components:"
echo -e "   • Raspberry Pi 4"
echo -e "   • Camera Module 5MP"  
echo -e "   • MG996R Servo Motor"
echo -e "   • L298N Motor Driver"
echo -e "   • FC-51 IR Sensor"
echo -e "   • LM2596 Buck Converter"
echo -e "   • 12V/5A Power Supply"

# Check 6: GPIO Access
echo -e "\n${YELLOW}🔌 Checking GPIO Access...${NC}"
if [ -d "venv" ]; then
    source venv/bin/activate
    python3 -c "
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()
    print('   ✅ GPIO access OK')
except Exception as e:
    print(f'   ❌ GPIO access failed: {e}')
    print('   💡 Try running with: sudo')
" 2>/dev/null
else
    echo -e "   ⚠️  Cannot test GPIO (no virtual environment)"
fi

# Check 7: Camera Access
echo -e "\n${YELLOW}📷 Checking Camera Access...${NC}"
if command -v libcamera-hello >/dev/null 2>&1; then
    echo -e "   ✅ libcamera tools available"
else
    echo -e "   ❌ libcamera tools missing"
    echo -e "   💡 Run: sudo apt install libcamera-apps"
fi

# Check 8: System Services
echo -e "\n${YELLOW}🔄 Checking System Configuration...${NC}"
# Check if camera is enabled
if [ -f /boot/config.txt ]; then
    if grep -q "^camera_auto_detect=1" /boot/config.txt || grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
        echo -e "   ✅ Camera interface likely enabled"
    else
        echo -e "   ⚠️  Camera interface may not be enabled"
        echo -e "   💡 Run: sudo raspi-config"
    fi
fi

# Summary
echo -e "\n" + "="*60
echo -e "${BLUE}📊 SUMMARY${NC}"
echo "="*60

if [ ${#missing_files[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All core files present${NC}"
else
    echo -e "${RED}❌ Missing files: ${missing_files[*]}${NC}"
fi

if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Virtual environment ready${NC}"
else
    echo -e "${RED}❌ Virtual environment needs setup${NC}"
fi

if [ -f ".env" ]; then
    echo -e "${GREEN}✅ Configuration file present${NC}"
else
    echo -e "${RED}❌ Configuration needs setup${NC}"
fi

echo -e "\n${YELLOW}🚀 Next Steps:${NC}"
if [ ! -d "venv" ] || [ ${#missing_files[@]} -ne 0 ]; then
    echo -e "   1. Run: ${GREEN}./start.sh${NC} (setup system)"
    echo -e "   2. Configure .env file with your settings"
    echo -e "   3. Test hardware: ${GREEN}python3 test_hardware.py${NC}"
    echo -e "   4. Run system: ${GREEN}./run.sh${NC}"
else
    echo -e "   1. Test hardware: ${GREEN}python3 test_hardware.py${NC}"
    echo -e "   2. Test IR sensor: ${GREEN}python3 test_ir_sensor.py${NC}"
    echo -e "   3. Check connection: ${GREEN}python3 test_connection.py${NC}"
    echo -e "   4. Run system: ${GREEN}./run.sh${NC}"
fi

echo -e "\n${BLUE}📖 Documentation:${NC}"
echo -e "   • Hardware guide: ${GREEN}python3 hardware_guide.py${NC}"
echo -e "   • Setup guide: ${GREEN}cat SETUP_GUIDE.md${NC}"

echo ""
echo "="*60