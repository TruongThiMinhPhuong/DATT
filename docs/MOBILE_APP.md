# 📱 Mobile App Guide

Hướng dẫn setup và sử dụng Flutter mobile app.

---

## 🎯 Tính năng

- **Dashboard**: Thống kê real-time
- **History**: Xem lại tất cả phân loại với ảnh
- **Settings**: Quản lý tài khoản, thông báo
- **Offline**: Cache dữ liệu khi mất mạng

---

## 🔧 Setup

### 1. Install Flutter

**Windows:**
```bash
# Download từ: https://flutter.dev/docs/get-started/install/windows
flutter doctor
```

**macOS:**
```bash
brew install flutter
flutter doctor
```

### 2. Setup Project

```bash
cd mobile_app

# Get dependencies
flutter pub get

# Check setup
flutter doctor
```

### 3. Add Firebase Config

**Android:**
```bash
# Download từ Firebase Console
# Place vào: android/app/google-services.json
```

**iOS:**
```bash
# Download từ Firebase Console
# Place vào: ios/Runner/GoogleService-Info.plist
```

### 4. Configure Backend URL

Edit `lib/services/api_service.dart`:
```dart
ApiService({this.baseUrl = 'http://YOUR_SERVER_IP:8000'});
```

---

## 🚀 Run & Build

### Development
```bash
# Run on connected device
flutter run

# Hot reload: Press 'r'
# Hot restart: Press 'R'
```

### Android Release
```bash
# Build APK
flutter build apk --release

# Output: build/app/outputs/flutter-apk/app-release.apk

# Install on device
flutter install
```

### iOS Release (Requires Mac)
```bash
# Build
flutter build ios --release

# Archive in Xcode
open ios/Runner.xcworkspace
```

---

## 📱 Screens

### Dashboard
- Statistics (Fresh/Spoiled/Other/Total)
- Recent classifications
- Pull to refresh
- Real-time updates

### History
- All classifications
- Filter by category
- Image gallery
- Zoom images
- Relative time

### Settings
- User account
- Sign in/out
- Notifications
- App info

---

## 🔐 Authentication

### Sign In
1. Tap "Sign In" in Settings
2. Choose Google Sign In
3. Select account
4. Grant permissions

### Admin Features
Admin users see additional features:
- Hardware controls (future)
- System settings (future)

---

## 🔔 Push Notifications

### Setup
1. Firebase Console → Cloud Messaging
2. Copy Server Key
3. Add to backend

### Test
```bash
# From backend
python send_test_notification.py
```

---

## 🎨 Customization

### Change Theme
Edit `lib/main.dart`:
```dart
theme: ThemeData(
  primarySwatch: Colors.blue,  // Change color
  useMaterial3: true,
),
```

### Change App Icon
```bash
# Edit: assets/icons/app_icon.png
flutter pub run flutter_launcher_icons
```

### Change App Name
**Android:** `android/app/src/main/AndroidManifest.xml`
```xml
<application android:label="Your App Name">
```

**iOS:** `ios/Runner/Info.plist`
```xml
<key>CFBundleName</key>
<string>Your App Name</string>
```

---

## 🐛 Troubleshooting

### "MissingPluginException"
```bash
flutter clean
flutter pub get
flutter run
```

### "Firebase not initialized"
```bash
# Check google-services.json exists
ls android/app/google-services.json

# Re-download from Firebase Console if missing
```

### Build errors
```bash
# Clean build
flutter clean
rm -rf build/

# Rebuild
flutter pub get
flutter build apk
```

---

## 📊 Project Structure

```
mobile_app/
├── lib/
│   ├── main.dart                 # Entry point
│   ├── screens/
│   │   ├── dashboard_screen.dart # Main dashboard
│   │   ├── history_screen.dart   # History list
│   │   └── settings_screen.dart  # Settings
│   ├── services/
│   │   ├── firebase_service.dart # Firebase integration
│   │   └── api_service.dart      # REST API client
│   └── widgets/
│       └── stat_card.dart        # Reusable widget
├── android/                      # Android config
├── ios/                          # iOS config
└── pubspec.yaml                  # Dependencies
```

---

## 🔧 Development Tips

### Hot Reload
- Press `r` để reload UI
- Press `R` để restart app
- Press `q` để thoát

### Debug Mode
```dart
// Add debug prints
print('Value: $value');

// Use debugger
debugger();
```

### Performance
```bash
# Profile mode
flutter run --profile

# Check performance
flutter run --trace-startup
```

---

## 📦 Dependencies

Main packages:
- `firebase_core` - Firebase SDK
- `cloud_firestore` - Database
- `firebase_storage` - Image storage
- `firebase_auth` - Authentication
- `provider` - State management
- `fl_chart` - Charts
- `cached_network_image` - Image caching

---

## 🚀 Deployment

### Google Play Store
1. Create signing key
2. Build release APK
3. Upload to Play Console
4. Submit for review

### App Store
1. Enroll in Apple Developer Program
2. Build iOS release
3. Archive in Xcode
4. Upload to App Store Connect

---

## 💡 Best Practices

- Use `const` constructors
- Implement error handling
- Add loading states
- Cache network images
- Handle offline mode
- Test on real devices

---

**App đã sẵn sàng! 🎉**
