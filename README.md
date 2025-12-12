# 🍎 AI Fruit Classification System

Hệ thống phân loại trái cây tự động sử dụng AI, băng tải, và điều khiển từ xa.

---

## 📋 Tổng quan

**Tính năng chính:**
- 🤖 AI phân loại trái cây (Tươi/Hỏng/Khác)
- 🎥 Camera 5MP + xử lý ảnh nâng cao
- 🔧 Điều khiển phần cứng từ xa (Web + Mobile)
- ☁️ Lưu trữ đám mây Firebase
- 📱 Mobile app Android/iOS
- 🌐 Web dashboard real-time

---

## 🚀 Quick Start

### 1. Firebase Setup (5 phút)

```bash
1. Tạo project tại: https://console.firebase.google.com
2. Enable: Storage, Firestore, Authentication
3. Download firebase_config.json → backend/
4. Copy Firebase web config → dashboard/firebase-config.js
```

📖 Chi tiết: `docs/FIREBASE_SETUP.md`

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
python classifier_service.py  # Terminal 1
python api.py                 # Terminal 2
```

### 3. Raspberry Pi

```bash
cd raspberry-pi
pip install -r requirements.txt
chmod +x start.sh
./start.sh
```

### 4. Web Dashboard

```bash
cd dashboard
python -m http.server 3000
# Mở: http://localhost:3000
```

### 5. Mobile App

```bash
cd mobile_app
flutter pub get
flutter run
```

---

## 📁 Cấu trúc Project

```
DATT/
├── backend/              # Python FastAPI server
├── raspberry-pi/         # Code chạy trên Raspberry Pi
├── dashboard/            # Web dashboard
├── mobile_app/           # Flutter mobile app
└── docs/                 # Documentation
```

---

## 🔧 Phần cứng

- Raspberry Pi 4 (4GB RAM)
- Camera 5MP
- IR Sensor FC-51 (GPIO 24)
- Servo MG996R (GPIO 18)
- L298N Motor Driver (GPIO 17, 27, 22)
- Buck Converter LM2596 (6V cho servo)

📖 Chi tiết: `docs/HARDWARE_SETUP.md`

---

## 🌐 Tailscale Setup (Khuyến nghị)

**Dùng Tailscale cho IP cố định:**
- ✅ IP không đổi - Kết nối ổn định
- ✅ Kết nối từ xa - Ở đâu cũng được
- ✅ Bảo mật cao - WireGuard encryption

📖 Hướng dẫn: `docs/TAILSCALE_SETUP.md`

---

## 📚 Documentation

| File | Mô tả |
|------|-------|
| `docs/QUICK_START.md` | Hướng dẫn nhanh |
| `docs/FIREBASE_SETUP.md` | Setup Firebase |
| `docs/HARDWARE_SETUP.md` | Setup phần cứng |
| `docs/API_REFERENCE.md` | API documentation |
| `docs/MOBILE_APP.md` | Mobile app guide |

---

## 🎯 Tính năng

### ✅ Backend
- Firebase Cloud Storage
- Real-time classification
- Hardware control API
- WebSocket updates

### ✅ Raspberry Pi
- IR sensor detection
- Motor control (servo + conveyor)
- Flask control server
- Multi-mode triggering

### ✅ Web Dashboard
- Real-time statistics
- Hardware control panel
- Image gallery
- Admin authentication

### ✅ Mobile App
- Live dashboard
- History với images
- Settings & auth
- Offline support

---

## 🧪 Testing

```bash
# Backend
curl http://localhost:8000/api/health

# Raspberry Pi
curl http://raspberrypi.local:5000/status

# Mobile
flutter test
```

---

## 📊 System Status

**Completion**: ~90%
**Technologies**: Python, Flutter, Firebase, TensorFlow
**Platform**: Web, Android, iOS

---

## 👨‍💻 Development

```bash
# Install all dependencies
pip install -r backend/requirements.txt
pip install -r raspberry-pi/requirements.txt
flutter pub get

# Run tests
pytest backend/tests/
flutter test
```

---

## 🐛 Troubleshooting

**Firebase connection error?**
→ Check `firebase_config.json` exists

**Raspberry Pi unreachable?**
→ Ping: `ping raspberrypi.local`

**Mobile app build error?**
→ Run: `flutter clean && flutter pub get`

---

## 📝 License

MIT License - See LICENSE file

---

## 🆘 Support

Xem chi tiết tài liệu trong thư mục `docs/`
