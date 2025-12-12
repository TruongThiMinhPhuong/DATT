# Migration từ Firebase sang Supabase - Hoàn tất ✅

## Tóm tắt thay đổi

### 1. Backend (Python)
✅ **supabase_storage.py** - Module mới thay thế firebase_storage.py
✅ **config.py** - Cập nhật SUPABASE_URL, SUPABASE_KEY
✅ **requirements.txt** - Thay firebase-admin bằng supabase
✅ **database.py** - Đổi firebase_id → supabase_id
✅ **hardware_api.py** - Cập nhật comments về authentication
✅ **.env.example** - Thêm Supabase config

### 2. Dashboard (Web)
✅ **supabase-config.js** - File mới thay thế firebase-config.js
✅ **index.html** - Import supabase-config.js thay vì firebase-config.js

### 3. Mobile App (Flutter)
✅ **pubspec.yaml** - Thay các Firebase packages bằng supabase_flutter
✅ **main.dart** - Supabase.initialize() thay Firebase.initializeApp()
✅ **supabase_service.dart** - Service mới thay firebase_service.dart
✅ **dashboard_screen.dart** - Sử dụng SupabaseService
✅ **history_screen.dart** - Consumer<SupabaseService> thay StreamBuilder
✅ **settings_screen.dart** - Supabase Auth thay Firebase Auth

### 4. Documentation
✅ **SUPABASE_SETUP.md** - Hướng dẫn setup hoàn chỉnh
✅ **README.md** - Cập nhật references
✅ **COMPLETE_GUIDE.md** - Cập nhật architecture
✅ **API_REFERENCE.md** - Cập nhật auth token



## Bước tiếp theo

### 1. Setup Supabase Project
```bash
1. Tạo account tại https://supabase.com
2. Tạo project mới
3. Lấy Project URL và API keys
```

### 2. Tạo Database Tables
```sql
-- Chạy trong SQL Editor
CREATE TABLE classifications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    classification VARCHAR(50) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    device_id VARCHAR(100),
    image_url TEXT,
    image_path VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE users (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email VARCHAR(255),
    role VARCHAR(50) DEFAULT 'viewer',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3. Tạo Storage Bucket
```bash
1. Vào Storage trong Supabase Dashboard
2. Tạo bucket tên: fruit-images
3. Set là Public bucket
4. Cấu hình policies (xem SUPABASE_SETUP.md)
```

### 4. Cập nhật Config Files

**Backend (.env):**
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-service-role-key
```

**Dashboard (supabase-config.js):**
```javascript
const supabaseConfig = {
    url: 'https://xxxxx.supabase.co',
    anonKey: 'your-anon-key'
};
```

**Mobile App (lib/main.dart):**
```dart
await Supabase.initialize(
    url: 'https://xxxxx.supabase.co',
    anonKey: 'your-anon-key',
);
```

### 5. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Mobile:**
```bash
cd mobile_app
flutter pub get
```

### 6. Run & Test
```bash
# Backend
python backend/classifier_service.py
python backend/api.py

# Dashboard
cd dashboard
python -m http.server 3000

# Mobile
flutter run
```

## So sánh Firebase vs Supabase

| Tính năng | Firebase | Supabase |
|-----------|----------|----------|
| Database | Firestore (NoSQL) | PostgreSQL (SQL) |
| Storage | Cloud Storage | S3-compatible |
| Auth | Firebase Auth | GoTrue (PostgreSQL) |
| Realtime | Firestore Realtime | PostgreSQL Realtime |
| Free Tier | 1GB storage | 500MB DB + 1GB storage |
| Self-hosting | ❌ | ✅ |
| Open Source | ❌ | ✅ |
| Pricing | Pay as you go | More predictable |

## Ưu điểm của Supabase

1. **Open Source** - Có thể self-host
2. **SQL Database** - PostgreSQL mạnh mẽ, dễ query
3. **Row Level Security** - Bảo mật tốt hơn
4. **Realtime** - Built-in realtime cho mọi table
5. **Pricing** - Minh bạch, dễ dự đoán chi phí
6. **API Auto-generated** - RESTful API tự động từ database schema

## Troubleshooting

### Lỗi Import
```bash
# Nếu thiếu package
pip install supabase
flutter pub get
```

### Lỗi Authentication
```
- Kiểm tra API key đã đúng chưa (anon key cho frontend, service_role cho backend)
- Enable email provider trong Supabase Dashboard
```

### Lỗi RLS (Row Level Security)
```sql
-- Tắt tạm để test
ALTER TABLE classifications DISABLE ROW LEVEL SECURITY;
```

## Tài liệu tham khảo

- [docs/SUPABASE_SETUP.md](docs/SUPABASE_SETUP.md) - Setup chi tiết
- [Supabase Docs](https://supabase.com/docs)
- [Supabase Python Client](https://supabase.com/docs/reference/python)
- [Supabase Flutter](https://supabase.com/docs/reference/dart)
