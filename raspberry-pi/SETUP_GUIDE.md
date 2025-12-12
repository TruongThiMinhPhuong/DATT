# 🥧 Cấu hình Raspberry Pi - Hướng dẫn từng file

Chi tiết setup cho từng file trong thư mục `raspberry-pi/`

---

## 📋 Tổng quan files

```
raspberry-pi/
├── config.py              ⚙️ CẤU HÌNH CHÍNH - PHẢI SỬA
├── .env.example          📝 Template biến môi trường
├── main.py               ▶️ Chương trình chính
├── control_server.py     🌐 Server điều khiển từ xa
├── motor_controller.py   🔧 Điều khiển motor
├── camera_module.py      📷 Module camera
├── rabbitmq_client.py    📨 Kết nối RabbitMQ
├── start.sh              🚀 Script khởi động
├── test_ir_sensor.py     🧪 Test IR sensor
└── requirements.txt      📦 Dependencies
```

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
