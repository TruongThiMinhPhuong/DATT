# 🍓 Raspberry Pi Fruit Sorting System

Hệ thống phân loại trái cây tự động sử dụng AI trên Raspberry Pi với camera, servo motor, và băng tải.

## 🚀 Khởi Động Nhanh

```bash
# 1. Cài đặt hệ thống
./start.sh

# 2. Kiểm tra hệ thống  
./check_project.sh

# 3. Test phần cứng
python3 test_hardware.py

# 4. Chạy hệ thống
./run.sh
```

## 📁 Cấu Trúc Project

```
raspberry-pi/
├── 🚀 start.sh              # Script cài đặt hệ thống
├── 🏃 run.sh                # Chạy ứng dụng
├── 🔍 check_project.sh      # Kiểm tra tình trạng project
├── ⚙️  config.py            # Cấu hình GPIO, servo, camera
├── 🎯 main.py               # Ứng dụng chính
├── 📷 camera_module.py      # Module camera
├── 🔧 motor_controller.py   # Điều khiển servo + motor
├── 📨 rabbitmq_client.py    # Kết nối RabbitMQ
├── 🌐 control_server.py     # Web server điều khiển
├── 🧪 test_*.py            # Scripts kiểm tra
├── 📖 hardware_guide.py     # Hướng dẫn phần cứng
├── 📋 SETUP_GUIDE.md        # Hướng dẫn thiết lập
└── 📦 requirements.txt      # Python dependencies
```

## 🔧 Phần Cứng

- **Raspberry Pi 4** (4GB+ khuyến nghị)
- **Camera Module 5MP** (1080p)
- **MG996R Servo Motor** (6V, qua LM2596)
- **JGB37-545 DC Motor** + L298N Driver (12V)
- **FC-51 IR Sensor** (5V)
- **LM2596 Buck Converter** (12V→6V cho servo)
- **Adapter 12V/5A**

## 🔌 Kết Nối GPIO

| GPIO | Thành Phần |
|------|------------|
| 18   | Servo PWM  |
| 17   | L298N ENA  |
| 27   | L298N IN1  |
| 22   | L298N IN2  |
| 24   | IR Sensor  |

## 🎯 Quy Trình Hoạt Động

1. **IR Sensor** phát hiện trái cây
2. **Camera** chụp ảnh (delay 0.3s)
3. **RabbitMQ** gửi ảnh đến laptop AI
4. **Laptop** phân loại và trả kết quả
5. **Servo** xoay đến vị trí tương ứng
6. **Băng tải** tiếp tục vận chuyển

## 📊 Phân Loại

- **Trái (30°)**: Vật thể khác
- **Giữa (90°)**: Trái cây tươi  
- **Phải (150°)**: Trái cây hỏng

## ⚠️ Lưu Ý An Toàn

- **KHÔNG** nối servo trực tiếp 12V
- **KIỂM TRA** cực tính trước cấp nguồn
- **HIỆU CHUẨN** LM2596 output = 6.0V
- **SỬ DỤNG** cầu chì bảo vệ

## 🆘 Hỗ Trợ

```bash
# Chẩn đoán tổng thể
./check_project.sh

# Xem hướng dẫn phần cứng
python3 hardware_guide.py

# Test từng component
python3 test_hardware.py
python3 test_ir_sensor.py
python3 test_connection.py
```

---
*Hệ thống AI Phân loại Trái cây - Raspberry Pi Edge Module*