# 🍓 HƯỚNG DẪN THIẾT LẬP HỆ THỐNG PHÂN LOẠI TRÁI CÂY

## 📋 TỔNG QUAN

Hệ thống phân loại trái cây tự động sử dụng AI trên Raspberry Pi với các thành phần:
- **Camera**: Chụp ảnh trái cây
- **AI Backend**: Phân loại bằng machine learning  
- **Motors**: Servo + băng tải để phân loại
- **Sensors**: IR sensor phát hiện vật thể

## 🔧 PHẦN CỨNG CẦN THIẾT

### Thành phần chính:
- Raspberry Pi 4 (4GB+ RAM khuyến nghị)
- Camera Module 5MP
- MG996R Servo Motor
- JGB37-545 DC Motor + L298N Driver
- FC-51 IR Sensor
- LM2596 Buck Converter (12V→6V)
- Adapter 12V/5A

### Kết nối:
- Breadboard/PCB
- Jumper wires
- Terminal blocks
- Tụ điện 1000µF/16V

## ⚡ THIẾT LẬP NGUỒN ĐIỆN

```
Nguồn 12V/5A
├── Raspberry Pi ← USB-C 5V/3A
├── LM2596 (12V→6V) ← Servo MG996R
├── L298N (12V) ← Motor băng tải
└── IR Sensor ← 5V từ Pi
```

**LƯU Ý**: Điều chỉnh LM2596 output = 6.0V chính xác!

## 🔌 SƠ ĐỒ KẾT NỐI GPIO

| GPIO | Pin | Thành phần |
|------|-----|------------|
| 18   | 12  | Servo PWM  |
| 17   | 11  | L298N ENA  |
| 27   | 13  | L298N IN1  |
| 22   | 15  | L298N IN2  |
| 24   | 18  | IR Sensor  |
| 5V   | 2   | IR Sensor VCC |
| GND  | 6   | Common GND |

## 🚀 CÀI ĐẶT PHẦN MỀM

### Bước 1: Clone dự án
```bash
git clone <repository-url>
cd raspberry-pi
```

### Bước 2: Chạy script cài đặt
```bash
./start.sh
```

Script sẽ:
- Tăng swap space lên 4GB
- Cài đặt system packages
- Tạo virtual environment
- Cài Python packages
- Kích hoạt camera/GPIO

### Bước 3: Cấu hình
```bash
cp .env.example .env
nano .env  # Sửa RABBITMQ_HOST
```

## 🧪 KIỂM TRA HỆ THỐNG

### Kiểm tra tổng thể:
```bash
./check_project.sh
```

### Kiểm tra từng thành phần:
```bash
# Phần cứng
python3 test_hardware.py

# IR Sensor
python3 test_ir_sensor.py  

# Kết nối mạng
python3 test_connection.py

# Hướng dẫn phần cứng
python3 hardware_guide.py
```

## 🏃 CHẠY HỆ THỐNG

### Khởi động hệ thống:
```bash
./run.sh
```

### Tắt hệ thống:
```
Ctrl+C
```

## 🔧 HIỆU CHUẨN

### 1. LM2596 Buck Converter
- Đặt multimeter ở chế độ DC voltage
- Kết nối probe vào output LM2596  
- Xoay potentiometer đến 6.0V ±0.1V
- Test với servo kết nối

### 2. Servo Motor
- Kiểm tra góc quay: 0°, 90°, 180°
- Điều chỉnh `SERVO_ANGLE_*` trong config.py
- Test với: `python3 test_hardware.py`

### 3. IR Sensor
- Điều chỉnh độ nhạy bằng potentiometer
- Test phát hiện vật thể ở khoảng cách mong muốn
- Kiểm tra debounce time

## 🐛 KHẮC PHỤC LỖI

### Lỗi camera:
```bash
sudo raspi-config  # Enable camera
libcamera-hello    # Test camera
```

### Lỗi GPIO:
```bash
sudo usermod -a -G gpio pi
# Hoặc chạy với sudo
```

### Lỗi packages:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Lỗi RabbitMQ:
- Kiểm tra IP address laptop
- Đảm bảo RabbitMQ chạy trên laptop
- Test: `python3 test_connection.py`

## 📊 GIÁM SÁT

### Log files:
- System logs: `journalctl -f`
- Application logs: Hiển thị trên console

### Hiệu suất:
- CPU temperature: `vcgencmd measure_temp`
- Memory usage: `free -h`
- Disk space: `df -h`

## 🔄 QUY TRÌNH HOẠT ĐỘNG

1. **Khởi động**: Hệ thống init camera, motors, RabbitMQ
2. **Chờ**: IR sensor phát hiện vật thể
3. **Chụp**: Camera chụp ảnh sau delay
4. **Gửi**: Ảnh được gửi qua RabbitMQ đến laptop
5. **Phân loại**: AI model trên laptop phân loại
6. **Nhận**: Raspberry Pi nhận kết quả
7. **Phân loại**: Servo xoay, băng tải phân loại
8. **Lặp lại**: Quay về bước 2

## 🛡️ AN TOÀN

- **KHÔNG** kết nối servo trực tiếp 12V
- **LUÔN** kiểm tra cực tính trước cấp nguồn
- **SỬ DỤNG** cầu chì bảo vệ
- **KIỂM TRA** nhiệt độ LM2596 khi hoạt động
- **CÓ** nút emergency stop nếu cần

## 📞 HỖ TRỢ

Nếu gặp vấn đề:
1. Chạy `./check_project.sh` để chẩn đoán
2. Kiểm tra logs và error messages
3. Xem file hardware_guide.py
4. Test từng component riêng biệt

---

## 1. ⚙️ `config.py` - CẤU HÌNH CHÍNH

**⚠️ FILE QUAN TRỌNG NHẤT - PHẢI SỬA**

### Các thông số BẮT BUỘC phải sửa:

```python
# Dòng 12: Dùng IP Tailscale của laptop (khuyến nghị)
RABBITMQ_HOST = '100.64.1.2'  # ← IP Tailscale của backend laptop
```

**🌐 Khuyến nghị: Dùng Tailscale**
- ✅ IP cố định - Không bao giờ đổi
- ✅ Kết nối từ xa - Ở đâu cũng được
- ✅ Bảo mật cao - WireGuard
- 📖 Setup: `docs/TAILSCALE_SETUP.md`

**Cách lấy IP Tailscale:**
```bash
# Trên laptop
tailscale ip -4
# Output: 100.64.1.2
```

### Các thông số TÙY CHỌN (có thể điều chỉnh):

#### A. Chế độ trigger (Dòng 47)
```python
TRIGGER_MODE = 'ir_sensor'  # Chọn 1 trong 4 chế độ:
# 'ir_sensor'   - Dùng IR sensor (KHUYẾN NGHỊ)
# 'time_based'  - Chụp theo thời gian
# 'continuous'  - Chụp liên tục
# 'manual'      - Chụp thủ công qua API
```

#### B. GPIO Pins (Dòng 21-24, 52)
```python
SERVO_PIN = 18              # Servo motor
CONVEYOR_ENABLE_PIN = 17    # L298N Enable
CONVEYOR_IN1_PIN = 27       # L298N Input 1
CONVEYOR_IN2_PIN = 22       # L298N Input 2
IR_SENSOR_PIN = 24          # IR sensor
```

**Lưu ý:** Chỉ sửa nếu đấu nối khác so với hướng dẫn!

#### C. Góc servo (Dòng 27-29)
```python
SERVO_ANGLE_LEFT = 30      # Góc trái (cho "other")
SERVO_ANGLE_CENTER = 90    # Góc giữa (cho fresh) - đi thẳng
SERVO_ANGLE_RIGHT = 150    # Góc phải (cho spoiled)
```

**Hiệu chỉnh:** Chạy `motor_controller.py` để test và điều chỉnh

#### D. Tốc độ băng tải (Dòng 37)
```python
CONVEYOR_SPEED = 75  # 0-100% (khuyến nghị: 70-80)
```

#### E. Camera (Dòng 42-44)
```python
CAMERA_RESOLUTION = (1920, 1080)  # Full HD
CAMERA_FORMAT = 'RGB888'
CAMERA_WARMUP_TIME = 2  # Seconds
```

#### F. IR Sensor (Dòng 53)
```python
IR_DEBOUNCE_TIME = 2.0  # Thời gian giữa 2 lần phát hiện (giây)
```

**Điều chỉnh:** Tùy vào tốc độ băng tải và kích thước trái cây

---

## 2. 📝 `.env.example` → `.env`

**Bước 1:** Copy file
```bash
cp .env.example .env
```

**Bước 2:** Sửa `.env`
```bash
nano .env
```

**Nội dung cần sửa:**
```env
# IP máy backend (laptop)
RABBITMQ_HOST=192.168.1.100  # ← Thay IP của bạn

# Thông tin RabbitMQ (thường không cần sửa)
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_VHOST=/
```

**Lưu:** `Ctrl+O` → `Enter` → `Ctrl+X`

---

## 3. ▶️ `main.py` - CHƯƠNG TRÌNH CHÍNH

**Không cần sửa gì!** File này tự động đọc config từ `config.py`

**Cách chạy:**
```bash
# Chạy thông thường
python3 main.py

# Hoặc với sudo (nếu cần quyền GPIO)
sudo python3 main.py
```

**Tắt chương trình:** `Ctrl+C`

**Log:** Xem output trên terminal để theo dõi

---

## 4. 🌐 `control_server.py` - SERVER ĐIỀU KHIỂN

**Không cần sửa!** Tự động sử dụng config.

**Chức năng:** 
- Cho phép web dashboard điều khiển phần cứng từ xa
- Chạy trên port 5000

**Chạy riêng:**
```bash
python3 control_server.py
```

**Test:**
```bash
curl http://raspberrypi.local:5000/status
```

---

## 5. 🚀 `start.sh` - SCRIPT KHỞI ĐỘNG

**Không cần sửa!** Tự động khởi động cả 2 services.

**Cách dùng:**

**Bước 1:** Cho phép thực thi
```bash
chmod +x start.sh
```

**Bước 2:** Chạy
```bash
./start.sh
```

**Chức năng:**
1. Khởi động `control_server.py` ở background (port 5000)
2. Khởi động `main.py` (chương trình chính)

**Tắt:** 
- `Ctrl+C` → Tự động tắt cả 2 services
- Hoặc: `pkill -f control_server.py`

---

## 6. 🧪 `test_ir_sensor.py` - TEST IR SENSOR

**Không cần sửa!** Dùng để test IR sensor.

**Khi nào dùng:**
- Sau khi lắp IR sensor xong
- Khi cần hiệu chỉnh độ nhạy

**Cách dùng:**
```bash
sudo python3 test_ir_sensor.py
```

**Output:**
```
Testing IR Sensor on GPIO 24...
○ No object
○ No object
✓ Object DETECTED!  ← Khi có vật thể
○ No object
```

**Tắt:** `Ctrl+C`

**Điều chỉnh độ nhạy:**
- Xoay biến trở trên IR sensor (FC-51)
- LED xanh sáng = phát hiện vật thể
- Xoay cho phù hợp với khoảng cách cần thiết

---

## 7. 🔧 `motor_controller.py` - ĐIỀU KHIỂN MOTOR

**Không cần sửa!** Nhưng có thể chạy để test.

**Test motors:**
```bash
sudo python3 motor_controller.py
```

**Chức năng test:**
1. Test servo: Xoay trái → giữa → phải
2. Test conveyor: Start → Stop

**Dùng để:**
- Kiểm tra kết nối motor
- Hiệu chỉnh góc servo trong `config.py`
- Kiểm tra tốc độ băng tải

---

## 8. 📷 `camera_module.py` - MODULE CAMERA

**Không cần sửa!** Tự động chạy theo config.

**Không chạy trực tiếp!** Module này được `main.py` gọi.

**Kiểm tra camera:**
```bash
# Test camera bằng lệnh hệ thống
libcamera-hello

# Hoặc chụp ảnh test
libcamera-still -o test.jpg
```

---

## 9. 📨 `rabbitmq_client.py` - KẾT NỐI RABBITMQ

**Không cần sửa!** Tự động kết nối dựa trên config.

**Không chạy trực tiếp!** Module này được `main.py` gọi.

**Debug connection:**
- Kiểm tra `RABBITMQ_HOST` trong `config.py`
- Ping test: `ping 192.168.1.100`
- Check RabbitMQ trên backend: `curl http://192.168.1.100:15672`

---

## 10. 📦 `requirements.txt` - DEPENDENCIES

**Không cần sửa!** Chỉ dùng để install.

**Install tất cả dependencies:**
```bash
pip install -r requirements.txt
```

**Hoặc với sudo:**
```bash
sudo pip install -r requirements.txt
```

**Nội dung:**
- `picamera2` - Camera module
- `pika` - RabbitMQ client
- `RPi.GPIO` - GPIO control
- `Flask` - Web server cho control API
- `opencv-python` - Image processing
- `pillow` - Image handling

---

## ✅ CHECKLIST SETUP HOÀN CHỈNH

### Bước 1: Cài đặt hệ thống
```bash
cd raspberry-pi

# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy config
cp .env.example .env
```

### Bước 2: Cấu hình
```bash
# 3. Sửa config.py
nano config.py
# → Dòng 10: Sửa RABBITMQ_HOST

# 4. Sửa .env (tùy chọn)
nano .env
# → Sửa RABBITMQ_HOST nếu muốn
```

### Bước 3: Test từng phần
```bash
# 5. Test IR sensor
sudo python3 test_ir_sensor.py

# 6. Test motors
sudo python3 motor_controller.py

# 7. Test control server
python3 control_server.py &
curl http://localhost:5000/status
```

### Bước 4: Chạy hệ thống
```bash
# 8. Khởi động tự động
chmod +x start.sh
./start.sh
```

---

## 🔧 TROUBLESHOOTING

### Lỗi: "Failed to connect to RabbitMQ"
```bash
# Kiểm tra IP backend
ping 192.168.1.100  # Thay bằng IP của bạn

# Kiểm tra config
grep RABBITMQ_HOST config.py

# Sửa config
nano config.py
```

### Lỗi: "GPIO not found" / "Permission denied"
```bash
# Chạy với sudo
sudo python3 main.py

# Hoặc add user vào gpio group
sudo usermod -a -G gpio $USER
# Sau đó logout/login lại
```

### Lỗi: "Camera not found"
```bash
# Enable camera
sudo raspi-config
# → Interface Options → Camera → Enable

# Reboot
sudo reboot

# Test camera
libcamera-hello
```

### Lỗi: "Module not found"
```bash
# Cài lại dependencies
pip install -r requirements.txt --force-reinstall

# Hoặc từng package
pip install pika RPi.GPIO picamera2 Flask
```

---

## 📖 TÀI LIỆU THAM KHẢO

| File | Mục đích |
|------|----------|
| `config.py` | ⚙️ **Cấu hình chính - PHẢI SỬA** |
| `.env` | Biến môi trường (tùy chọn) |
| `start.sh` | Script khởi động tự động |
| `test_ir_sensor.py` | Test IR sensor |
| `motor_controller.py` | Test motors |

**Xem thêm:**
- `docs/QUICK_START.md` - Hướng dẫn nhanh
- `docs/HARDWARE_SETUP.md` - Sơ đồ kết nối
- `docs/IR_SENSOR_SETUP.md` - Chi tiết IR sensor

---

**🎯 Chỉ cần sửa 2 files:**
1. ✅ `config.py` - Dòng 10: RABBITMQ_HOST
2. ✅ `.env` - RABBITMQ_HOST (tùy chọn)

**Còn lại chỉ việc chạy!** 🚀
