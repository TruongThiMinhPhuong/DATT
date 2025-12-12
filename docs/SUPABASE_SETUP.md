# Supabase Setup Guide

## Bước 1: Tạo Supabase Project

1. Truy cập: https://supabase.com/
2. Click **"Start your project"** hoặc **"Sign In"**
3. Click **"New Project"**
4. Tên dự án: `fruit-classification-system`
5. Database Password: Tạo password mạnh (lưu lại!)
6. Region: `Southeast Asia (Singapore)` - gần VN
7. Click **"Create new project"**
8. Đợi 2-3 phút để project được khởi tạo

---

## Bước 2: Lấy API Keys

1. Vào **Project Settings** (⚙️ icon)
2. Tab **API**
3. Copy các thông tin sau:

```
Project URL: https://xxxxx.supabase.co
anon/public key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```
```
https://ibuvxatpxrqknpfmjzwq.supabase.co
anon/public key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlidXZ4YXRweHJxa25wZm1qendxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU1MzgzNTEsImV4cCI6MjA4MTExNDM1MX0.h2mJLtcbtKhkpEAzwnieatqyMyOTWptMqfYeYzDg4NE
service_role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlidXZ4YXRweHJxa25wZm1qendxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NTUzODM1MSwiZXhwIjoyMDgxMTE0MzUxfQ.FffqTRlmW2n_Z0SxGAjV0Q4YBoS8XKXXkmWRvvPJp7M
```
**⚠️ QUAN TRỌNG:**
- `anon key`: Dùng cho frontend (dashboard, mobile app)
- `service_role key`: Dùng cho backend (KHÔNG ĐƯỢC LỘ RA NGOÀI!)

---

## Bước 3: Tạo Database Tables

### 3.1 Vào SQL Editor

1. Sidebar → **SQL Editor**
2. Click **"New query"**
3. Paste và chạy các SQL sau:

### 3.2 Tạo bảng classifications

```sql
-- Classifications table
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

-- Index for faster queries
CREATE INDEX idx_classifications_timestamp ON classifications(timestamp DESC);
CREATE INDEX idx_classifications_classification ON classifications(classification);

-- Enable Row Level Security
ALTER TABLE classifications ENABLE ROW LEVEL SECURITY;

-- Policy: Allow public read
CREATE POLICY "Allow public read" ON classifications
    FOR SELECT USING (true);

-- Policy: Allow authenticated insert (for backend)
CREATE POLICY "Allow service role insert" ON classifications
    FOR INSERT WITH CHECK (true);
```

### 3.3 Tạo bảng users (cho role management)

```sql
-- Users table for role management
CREATE TABLE users (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    email VARCHAR(255),
    role VARCHAR(50) DEFAULT 'viewer',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can read their own data
CREATE POLICY "Users can read own data" ON users
    FOR SELECT USING (auth.uid() = id);
```

### 3.4 Click **"Run"** để thực thi

---

## Bước 4: Setup Storage

### 4.1 Tạo Storage Bucket

1. Sidebar → **Storage**
2. Click **"New bucket"**
3. Bucket name: `fruit-images`
4. ✅ Check **"Public bucket"**
5. Click **"Create bucket"**

### 4.2 Storage Policies

**⚠️ Quan trọng**: Phải cấu hình policies để cho phép upload và download ảnh!

#### Policy 1: Allow Public Read (Cho phép mọi người xem ảnh)

1. Click vào bucket `fruit-images`
2. Tab **Policies**
3. Click **"New policy"**
4. Chọn **"For full customization"**
5. Điền thông tin:
   - **Policy name**: `Allow public read`
   - **Allowed operation**: ✅ Check **SELECT** (để download/xem ảnh)
   - **Target roles**: Để mặc định `Defaults to all (public) roles if none selected`
   - **Policy definition**: Paste dòng này vào (KHÔNG có dấu ```):
     ```
     bucket_id = 'fruit-images'
     ```
     ⚠️ **Chỉ paste dòng**: `bucket_id = 'fruit-images'` (không có ```sql)
6. Click **"Save policy"**

**Giải thích**: 
- Policy này cho phép **bất kỳ ai** (kể cả không đăng nhập) đều có thể **xem/download** ảnh từ bucket
- Cần thiết để Dashboard và Mobile app hiển thị ảnh

---

#### Policy 2: Allow Service Upload (Cho phép Backend upload ảnh)

1. Click **"New policy"** một lần nữa
2. Chọn **"For full customization"**
3. Điền thông tin:
   - **Policy name**: `Allow service upload`
   - **Allowed operation**: ✅ Check **INSERT** (để upload ảnh mới)
   - **Target roles**: Để mặc định `Defaults to all (public) roles if none selected`
   - **Policy definition**: Paste dòng này vào:
     ```
     bucket_id = 'fruit-images'
     ```
     ⚠️ **Chỉ paste**: `bucket_id = 'fruit-images'` (không có dấu backticks)
4. Click **"Save policy"**

**Giải thích**:
- Policy này cho phép **upload** ảnh vào bucket
- Backend sẽ dùng `service_role` key nên có quyền upload

---

#### Policy 3 (Optional): Allow Authenticated Delete

Nếu muốn user có thể xóa ảnh của mình:

1. Click **"New policy"**
2. Chọn **"For full customization"**
3. Điền:
   - **Policy name**: `Allow authenticated delete`
   - **Allowed operation**: ✅ Check **DELETE**
   - **Target roles**: Chọn Paste dòng này vào:
     ```
     bucket_id = 'fruit-images' AND auth.role() = 'authenticated'
     ```
     ⚠️ **Chỉ paste**: `bucket_id = 'fruit-images' AND auth.role() = 'authenticated'cket_id = 'fruit-images' AND auth.role() = 'authenticated'
     ```
4. Click **"Save policy"**

---

#### Cách Test Policies

**Test từ Browser Console**:
```javascript
// Test public read (nên thành công)
const { data, error } = await supabase.storage
    .from('fruit-images')
    .getPublicUrl('images/test.jpg');
console.log(data.publicUrl);

// Test upload với anon key (nên thành công vì policy cho phép)
const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
const { error: uploadError } = await supabase.storage
    .from('fruit-images')
    .upload('images/test.jpg', file);
console.log(uploadError);
```

**Test từ Backend (Python)**:
```python
# Test upload với service_role key
result = supabase.storage.from_('fruit-images').upload(
    'images/test.jpg',
    open('test.jpg', 'rb').read(),
    file_options={"content-type": "image/jpeg"}
)
print(result)

# Test get public URL
url = supabase.storage.from_('fruit-images').get_public_url('images/test.jpg')
print(url)
```

---

#### ✅ Checklist Policies

Sau khi setup xong, kiểm tra:
- [ ] Policy "Allow public read" với SELECT operation
- [ ] Policy "Allow service upload" với INSERT operation
- [ ] Test upload từ Backend thành công
- [ ] Test view ảnh từ public URL thành công
- [ ] Policies hiển thị trong tab Policies của bucket

**Lỗi thường gặp**:
- ❌ "new row violates row-level security policy" → Check policy definition
- ❌ "permission denied for table storage.objects" → Chưa enable policy
- ❌ "storage/unauthorized" → Check bucket_id trong policy definition

---

## Bước 5: Setup Authentication

### 5.1 Enable Providers

1. Sidebar → **Authentication**
2. Tab **Providers**
3. Enable **Email**:
   - Toggle ON
   - ✅ Confirm email (optional)
4. Enable **Google** (optional):
   - Toggle ON
   - Client ID: Từ Google Cloud Console
   - Client Secret: Từ Google Cloud Console

### 5.2 Tạo Admin User

1. Tab **Users**
2. Click **"Add user"** → **"Create new user"**
3. Email: admin@example.com
4. Password: your-secure-password
5. ✅ Auto Confirm User
6. Click **"Create user"**
7. Copy **User UID**

8. Vào **SQL Editor**, chạy:
```sql
INSERT INTO users (id, email, role)
VALUES ('paste-user-uid-here', 'admin@example.com', 'admin');
```

---

## Bước 6: Cấu hình Project

### 6.1 Backend (Python)

Tạo file `.env` trong thư mục `backend/`:

```env
# Supabase Configuration
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-service-role-key

# Các config khác giữ nguyên...
RABBITMQ_HOST=localhost
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=phuong123
```

### 6.2 Dashboard (Web)

Sửa file `dashboard/supabase-config.js`:

```javascript
const supabaseConfig = {
    url: 'https://xxxxx.supabase.co',
    anonKey: 'your-anon-key'
};
```

### 6.3 Mobile App (Flutter)

Sửa file `mobile_app/lib/main.dart`:

```dart
await Supabase.initialize(
    url: 'https://xxxxx.supabase.co',
    anonKey: 'your-anon-key',
);
```

---

## Bước 7: Enable Realtime (Optional)

Để nhận cập nhật real-time:

1. Sidebar → **Database** → **Replication**
2. Tìm bảng `classifications`
3. Toggle ON để enable realtime
4. Hoặc chạy SQL:

```sql
ALTER PUBLICATION supabase_realtime ADD TABLE classifications;
```

---

## So sánh Firebase vs Supabase

| Feature | Firebase | Supabase |
|---------|----------|----------|
| Database | Firestore (NoSQL) | PostgreSQL (SQL) |
| Storage | Cloud Storage | S3-compatible |
| Auth | Firebase Auth | GoTrue Auth |
| Realtime | Firestore Realtime | PostgreSQL Realtime |
| Pricing | Pay as you go | Free tier + Pay as you go |
| Self-host | ❌ | ✅ |
| Open Source | ❌ | ✅ |

---

## Troubleshooting

### Lỗi "Invalid API Key"
- Kiểm tra key đã copy đúng chưa
- Đảm bảo dùng đúng key (anon cho frontend, service_role cho backend)

### Lỗi "Permission denied"
- Kiểm tra RLS policies
- Đảm bảo user đã được authenticate

### Lỗi Upload Storage
- Kiểm tra bucket policies
- Kiểm tra bucket có public không
- File size limit: 50MB (default)

### Realtime không hoạt động
- Kiểm tra table đã được add vào replication chưa
- Kiểm tra connection WebSocket

---

## Tài liệu tham khảo

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [Supabase Flutter Client](https://supabase.com/docs/reference/dart/introduction)
- [Supabase JavaScript Client](https://supabase.com/docs/reference/javascript/introduction)
