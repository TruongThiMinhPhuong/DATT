# 📋 Final Checklist

Để hoàn thành hệ thống, làm theo các bước sau:

---

## ✅ Backend (Completed)

- [x] Install dependencies: `pip install -r backend/requirements.txt`
- [x] Firebase integration code
- [x] Hardware API endpoints
- [x] Database schema updated
- [ ] **TODO: Setup Firebase** (follow `docs/FIREBASE_SETUP.md`)
  - Download `firebase_config.json`
  - Place in `backend/`

---

## ✅ Raspberry Pi (Completed)

- [x] Install dependencies: `pip install -r raspberry-pi/requirements.txt`
- [x] Control server created
- [x] Startup script ready
- [ ] **TODO: Configure**
  - Edit `config.py` with backend IP
  - Test IR sensor: `sudo python3 test_ir_sensor.py`
  - Run: `./start.sh`

---

## ✅ Web Dashboard (Completed)

- [x] Firebase SDK integrated
- [x] Authentication UI
- [x] Hardware control panel
- [ ] **TODO: Configure Firebase**
  - Copy web config from Firebase Console
  - Update `dashboard/firebase-config.js`
  - Replace YOUR_API_KEY, YOUR_PROJECT_ID, etc.

---

## ✅ Mobile App (Completed)

- [x] Flutter project structure
- [x] All screens (Dashboard, History, Settings)
- [x] Firebase & API services
- [ ] **TODO: Configure Firebase**
  - Download `google-services.json` → `android/app/`
  - Download `GoogleService-Info.plist` → `ios/Runner/`
  - Run: `flutter pub get`
  - Build: `flutter build apk`

---

## 🚀 Deployment Steps

### 1. Setup Firebase (15 minutes)
```bash
1. Go to https://console.firebase.google.com
2. Create project: "fruit-classification-system"
3. Enable: Storage, Firestore, Authentication, Cloud Messaging
4. Download service account key → backend/firebase_config.json
5. Copy web config → dashboard/firebase-config.js
6. Download google-services.json → mobile_app/android/app/
7. Download GoogleService-Info.plist → mobile_app/ios/Runner/
```

See: `docs/FIREBASE_SETUP.md`

### 2. Start Backend (2 minutes)
```bash
cd backend
python classifier_service.py  # Terminal 1
python api.py                 # Terminal 2
```

### 3. Start Raspberry Pi (1 minute)
```bash
cd raspberry-pi
./start.sh
```

### 4. Open Web Dashboard (30 seconds)
```bash
cd dashboard
python -m http.server 3000
# Open: http://localhost:3000
```

### 5. Run Mobile App (2 minutes)
```bash
cd mobile_app
flutter run
```

---

## ✅ Testing

### Backend
```bash
curl http://localhost:8000/api/health
# Expected: {"status":"healthy"}

curl http://localhost:8000/api/stats
# Expected: {"total":0,...}
```

### Raspberry Pi
```bash
curl http://raspberrypi.local:5000/status
# Expected: {"status":"online",...}
```

### Web Dashboard
1. Open http://localhost:3000
2. Click "Sign In"
3. Sign in with Google
4. Check statistics display

### Mobile App
1. Open app
2. View Dashboard tab
3. View History tab
4. View Settings tab

---

## 🎯 System Ready!

Sau khi hoàn thành checklist:
- ✅ Backend running on port 8000
- ✅ Raspberry Pi running control server on port 5000
- ✅ Web dashboard on port 3000
- ✅ Mobile app on device
- ✅ Firebase cloud storage active

**Hệ thống sẵn sàng phân loại trái cây! 🍎🍏**

---

## 📚 Documentation

| Guide | Purpose |
|-------|---------|
| `README.md` | Quick overview |
| `docs/QUICK_START.md` | 15-minute setup |
| `docs/FIREBASE_SETUP.md` | Firebase configuration |
| `docs/HARDWARE_SETUP.md` | Wiring diagrams |
| `docs/MOBILE_APP.md` | Flutter app guide |
| `docs/API_REFERENCE.md` | API documentation |

---

**Need help? Check the docs/ folder!**
