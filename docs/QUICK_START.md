# 🚀 Quick Start Guide

Hướng dẫn chạy hệ thống trong 15 phút.

---

## Bước 1: Setup RabbitMQ (5 phút)

### 1.1 Cài RabbitMQ

**Windows - Chocolatey (Khuyến nghị):**
```powershell
# PowerShell as Administrator
choco install rabbitmq -y
```

**Windows - Manual:**
1. Download Erlang: https://www.erlang.org/downloads
2. Download RabbitMQ: https://www.rabbitmq.com/docs/install-windows
3. Cài Erlang → Cài RabbitMQ

**Linux:**
```bash
sudo apt-get install rabbitmq-server -y
sudo systemctl start rabbitmq-server
```

**macOS:**
```bash
brew install rabbitmq
brew services start rabbitmq
```

### 1.2 Enable Management UI

**Windows:**
```powershell
cd "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.13.0\sbin"
.\rabbitmq-plugins.bat enable rabbitmq_management
net stop RabbitMQ
net start RabbitMQ
```

**Linux/Mac:**
```bash
sudo rabbitmq-plugins enable rabbitmq_management
sudo systemctl restart rabbitmq-server  # Linux
# hoặc
brew services restart rabbitmq  # Mac
```

### 1.3 Test

**Mở browser:** http://localhost:15672

**Login:** guest / guest

✅ Thấy RabbitMQ Management UI = Success!

📖 Chi tiết: `docs/RABBITMQ_SETUP.md`

---

## Bước 2: Setup Firebase (5 phút)

### 1.1 Tạo Firebase Project
1. Truy cập https://console.firebase.google.com
2. Click **"Add project"**
3. Tên: `fruit-classification-system`
4. Click **"Create project"**

### 1.2 Enable Services
- **Storage**: Sidebar → Storage → Get started → Production mode → asia-southeast1
- **Firestore**: Sidebar → Firestore → Create database → Production mode → asia-southeast1
- **Authentication**: Sidebar → Authentication → Get started → Enable Google & Email/Password

### 1.3 Download Credentials
**Backend:**
1. Project settings → Service accounts
2. Generate new private key
3. Save as `backend/firebase_config.json`

**Web:**
1. Project settings → General → Your apps
2. Add web app
3. Copy config → Paste vào `dashboard/firebase-config.js`

📖 Chi tiết: `FIREBASE_SETUP.md`

---

## Bước 3: Backend (2 phút)

```bash
cd backend

# Install
pip install -r requirements.txt

# Start
python classifier_service.py  # Terminal 1
python api.py                 # Terminal 2

# Test
curl http://localhost:8000/api/health
```

**Ports:**
- API: 8000
- RabbitMQ: 5672

---

## Bước 4: Raspberry Pi (3 phút)

```bash
cd raspberry-pi

# Install
pip install -r requirements.txt

# Config
nano config.py
# Sửa RABBITMQ_HOST = "192.168.1.100"  # IP máy backend

# Start
chmod +x start.sh
./start.sh

# Test
curl http://raspberrypi.local:5000/status
```

**Ports:**
- Control Server: 5000

---

## Bước 5: Web Dashboard (1 phút)

```bash
cd dashboard

# Update Firebase config
nano firebase-config.js
# Paste config từ Firebase Console

# Serve
python -m http.server 3000

# Mở browser
http://localhost:3000
```

---

## Bước 6: Mobile App (4 phút)

```bash
cd mobile_app

# Install dependencies
flutter pub get

# Add Firebase config
# Android: android/app/google-services.json
# iOS: ios/Runner/GoogleService-Info.plist

# Run
flutter run

# Build APK
flutter build apk --release
```

---

## ✅ Kiểm tra

### Backend
```bash
curl http://localhost:8000/api/stats
# Response: {"total":0,"category_counts":{}}
```

### Raspberry Pi
```bash
# Test IR sensor
sudo python3 test_ir_sensor.py

# Test motors
sudo python3 motor_controller.py
```

### Web Dashboard
1. Mở http://localhost:3000
2. Sign in với Google
3. Kiểm tra statistics hiển thị

### Mobile App
1. Mở app
2. Xem dashboard
3. Tab History
4. Tab Settings

---

## 🎯 Luồng hoạt động

```
1. Trái cây đi qua IR sensor
2. Raspberry Pi chụp ảnh
3. Gửi qua RabbitMQ → Backend
4. AI phân loại
5. Upload lên Firebase Storage
6. Lưu kết quả vào Firestore
7. Web dashboard cập nhật real-time
8. Mobile app nhận push notification
9. Servo xoay để phân loại
10. Băng tải tiếp tục
```

---

## 🐛 Xử lý lỗi thường gặp

### "Failed to connect to RabbitMQ"
```bash
# Kiểm tra RabbitMQ chạy chưa
systemctl status rabbitmq-server

# Start RabbitMQ
sudo systemctl start rabbitmq-server
```

### "Firebase config not found"
```bash
# Kiểm tra file tồn tại
ls backend/firebase_config.json

# Nếu không có → Download lại từ Firebase Console
```

### "Raspberry Pi unreachable"
```bash
# Ping
ping raspberrypi.local

# Nếu không ping được, dùng IP
ping 192.168.1.xxx
```

### "Module not found"
```bash
# Cài lại dependencies
pip install -r requirements.txt --force-reinstall
```

---

## 📱 Demo

**Chạy full system:**
```bash
# Terminal 1 - Backend
cd backend && python classifier_service.py

# Terminal 2 - API
cd backend && python api.py

# Terminal 3 - Web
cd dashboard && python -m http.server 3000

# Terminal 4 - Pi (trên Raspberry Pi)
cd raspberry-pi && ./start.sh

# Terminal 5 - Mobile
cd mobile_app && flutter run
```

---

## 🎓 Tiếp theo

- Đọc `API_REFERENCE.md` để hiểu API
- Xem `HARDWARE_SETUP.md` cho phần cứng
- Tham khảo `MOBILE_APP.md` để custom app

**Hệ thống đã sẵn sàng! 🎉**
