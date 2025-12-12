# 🔧 Cách Vận Hành Hệ Thống - System Overview

## 📊 Tổng Quan Kiến Trúc

```
┌─────────────────────────────────────────────────────────────────┐
│                        NGƯỜI DÙNG                               │
│         Web Dashboard        |        Mobile App                │
└──────────┬──────────────────┴──────────────────┬───────────────┘
           │                                      │
           │ HTTP/WebSocket                       │ HTTP/Supabase
           │                                      │
┌──────────▼──────────────────────────────────────▼───────────────┐
│                      SUPABASE CLOUD                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Database   │  │   Storage    │  │     Auth     │          │
│  │ (PostgreSQL) │  │  (S3-like)   │  │   (GoTrue)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└──────────────────────────────────────────────────────────────────┘
           │                                      │
           │ REST API                             │ Supabase SDK
           │                                      │
┌──────────▼──────────────────────────────────────▼───────────────┐
│                    BACKEND SERVER (Máy tính)                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  FastAPI Server (api.py) - Port 8000                      │  │
│  │  - REST API endpoints                                     │  │
│  │  - WebSocket cho real-time updates                       │  │
│  │  - Hardware control API                                   │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Classifier Service (classifier_service.py)               │  │
│  │  - TensorFlow/Keras model                                │  │
│  │  - Image processing                                       │  │
│  │  - Phân loại trái cây                                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  SQLite Database (local cache)                            │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           │ RabbitMQ (Message Queue)
                           │ Port 5672
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│                  RASPBERRY PI (Edge Device)                      │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Main Application (main.py)                               │  │
│  │  - Camera capture                                         │  │
│  │  - IR sensor monitoring                                   │  │
│  │  - Send images to Backend                                 │  │
│  │  - Receive classification results                         │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Control Server (control_server.py) - Flask Port 5000    │  │
│  │  - Remote hardware control                                │  │
│  │  - Status monitoring                                      │  │
│  └───────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Motor Controller (motor_controller.py)                   │  │
│  │  - Servo MG996R (GPIO 18)                                │  │
│  │  - DC Motor via L298N (GPIO 17, 27, 22)                 │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           │ GPIO Pins
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│                    PHẦN CỨNG (Hardware)                          │
│                                                                  │
│  Camera 5MP ───► Chụp ảnh trái cây                             │
│  IR Sensor ────► Phát hiện vật thể (GPIO 24)                   │
│  Servo Motor ──► Điều hướng trái cây (tươi/hỏng)               │
│  DC Motor ─────► Băng tải chuyền                                │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Quy Trình Hoạt Động (Workflow)

### 1. **Khởi Động Hệ Thống**

#### Backend (Máy tính):
```bash
# Terminal 1: Classifier Service
cd backend
python classifier_service.py

# Terminal 2: API Server
python api.py
```

#### Raspberry Pi:
```bash
# Terminal 1: Main Application
./start.sh

# Hoặc thủ công:
python main.py
```

### 2. **Quy Trình Phân Loại (Main Flow)**

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. IR SENSOR PHÁT HIỆN                                          │
│    - IR sensor (GPIO 24) phát hiện vật thể                     │
│    - Raspberry Pi: "Fruit detected!"                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. CHỤP ẢNH                                                     │
│    - Camera 5MP chụp ảnh (1920x1080)                           │
│    - Lưu tạm thời vào RAM                                       │
│    - Convert sang JPEG, resize 224x224                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. GỬI SANG BACKEND QUA RABBITMQ                               │
│    - Encode image thành hex string                              │
│    - Tạo message JSON:                                          │
│      {                                                           │
│        "image": "hex_data...",                                  │
│        "metadata": {                                            │
│          "device_id": "rpi_01",                                │
│          "timestamp": 1702345678.5                              │
│        }                                                         │
│      }                                                           │
│    - Publish vào queue: "fruit_images"                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. BACKEND XỬ LÝ (classifier_service.py)                       │
│    a) Nhận message từ RabbitMQ queue                           │
│    b) Decode hex → image bytes                                  │
│    c) Preprocessing:                                            │
│       - Resize to 224x224                                       │
│       - Normalize pixel values (0-1)                            │
│       - Add batch dimension                                     │
│    d) Chạy AI Model (TensorFlow):                              │
│       - MobileNetV2 backbone                                    │
│       - Output: [fresh_fruit, spoiled_fruit, other]           │
│    e) Post-processing:                                          │
│       - Lấy class có confidence cao nhất                        │
│       - Tính image quality metrics                              │
│       - Generate recommendations                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. LƯU KẾT QUẢ                                                 │
│    a) Lưu vào SQLite (local):                                  │
│       - Classification result                                   │
│       - Confidence score                                        │
│       - Processing time                                         │
│       - Device info                                             │
│    b) Upload lên Supabase:                                     │
│       - Image → Supabase Storage (bucket: fruit-images)        │
│       - Metadata → Supabase Database (table: classifications)  │
│       - Return: image_url, record_id                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. GỬI KẾT QUẢ VỀ RASPBERRY PI                                │
│    - Publish vào queue: "classification_results"               │
│    - Message:                                                   │
│      {                                                           │
│        "classification": "fresh_fruit",                        │
│        "confidence": 0.95,                                      │
│        "processing_time": 0.42,                                │
│        "image_url": "https://supabase.co/...",                │
│        "recommendation": "✅ Excellent quality"                │
│      }                                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. RASPBERRY PI NHẬN KẾT QUẢ                                  │
│    - Consume từ RabbitMQ queue                                 │
│    - Parse JSON result                                          │
│    - Log kết quả                                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. ĐIỀU KHIỂN SERVO                                            │
│    if classification == "fresh_fruit":                         │
│        servo.move("right")  # Hướng phải                       │
│    elif classification == "spoiled_fruit":                     │
│        servo.move("left")   # Hướng trái                       │
│    else:                                                        │
│        servo.move("center") # Giữa                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 9. CẬP NHẬT DASHBOARD (Real-time)                              │
│    - Backend broadcast qua WebSocket                            │
│    - Dashboard nhận update:                                     │
│      * Statistics counter tăng                                  │
│      * Chart cập nhật                                           │
│      * Activity feed thêm item mới                             │
│    - Mobile app nhận từ Supabase Realtime                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Chi Tiết Các Component

### A. **Backend Server** (Máy tính)

#### 1. **API Server (api.py)**
- **Port**: 8000
- **Chức năng**:
  - REST API endpoints:
    - `GET /api/stats` - Lấy thống kê
    - `GET /api/history` - Lịch sử phân loại
    - `POST /api/hardware/*` - Điều khiển phần cứng
  - WebSocket `/ws` - Real-time updates
  - Serve static files (Dashboard)

**Ví dụ API call**:
```bash
# Lấy thống kê
curl http://localhost:8000/api/stats

# Kết quả:
{
  "total": 150,
  "category_counts": {
    "fresh_fruit": 80,
    "spoiled_fruit": 50,
    "other": 20
  },
  "avg_confidence": 0.92
}
```

#### 2. **Classifier Service (classifier_service.py)**
- **Chức năng**:
  - Listen RabbitMQ queue "fruit_images"
  - Load AI model (TensorFlow/Keras)
  - Xử lý ảnh và phân loại
  - Publish kết quả vào "classification_results"

**Flow xử lý**:
```python
# 1. Nhận message
message = rabbitmq.consume("fruit_images")

# 2. Decode image
image_bytes = bytes.fromhex(message['image'])

# 3. Preprocessing
image = preprocess_image(image_bytes)  # 224x224x3

# 4. Predict
predictions = model.predict(image)
# [0.05, 0.92, 0.03] = [fresh, spoiled, other]

# 5. Get result
classification = "spoiled_fruit"  # Highest confidence
confidence = 0.92

# 6. Publish result
rabbitmq.publish("classification_results", {
    "classification": classification,
    "confidence": confidence
})
```

#### 3. **Supabase Storage (supabase_storage.py)**
- **Chức năng**:
  - Upload ảnh lên Supabase Storage
  - Lưu metadata vào Supabase Database
  - Tạo public URL cho ảnh

**Flow upload**:
```python
# 1. Upload image
result = supabase.storage.from_('fruit-images').upload(
    'images/20231212_143025_fresh.jpg',
    image_bytes
)

# 2. Get public URL
url = supabase.storage.from_('fruit-images').get_public_url(
    'images/20231212_143025_fresh.jpg'
)

# 3. Save to database
supabase.table('classifications').insert({
    'timestamp': '2023-12-12T14:30:25',
    'classification': 'fresh_fruit',
    'confidence': 0.92,
    'image_url': url
})
```

---

### B. **Raspberry Pi** (Edge Device)

#### 1. **Main Application (main.py)**
- **Chức năng chính**:
  - Monitor IR sensor
  - Capture image khi phát hiện
  - Send qua RabbitMQ
  - Nhận kết quả
  - Điều khiển servo

**Trigger Modes**:
```python
# Mode 1: IR Sensor (Mặc định)
if ir_sensor.is_detected():
    image = camera.capture()
    send_to_backend(image)

# Mode 2: Time-based
while True:
    image = camera.capture()
    send_to_backend(image)
    time.sleep(5)  # Mỗi 5 giây

# Mode 3: Continuous
while True:
    image = camera.capture()
    send_to_backend(image)

# Mode 4: Manual
# Chờ lệnh từ Dashboard
```

#### 2. **Control Server (control_server.py)**
- **Port**: 5000 (Flask)
- **Endpoints**:
  - `POST /control/conveyor/start` - Khởi động băng tải
  - `POST /control/conveyor/stop` - Dừng băng tải
  - `POST /control/conveyor/speed` - Đặt tốc độ
  - `POST /control/servo/move` - Di chuyển servo
  - `POST /control/camera/capture` - Chụp ảnh thủ công
  - `GET /status` - Trạng thái hệ thống

**Ví dụ**:
```bash
# Từ Dashboard gọi Backend API
curl -X POST http://localhost:8000/api/hardware/conveyor/start

# Backend forward đến Pi
curl -X POST http://100.64.1.3:5000/control/conveyor/start

# Pi thực thi
motor_controller.start_conveyor()
```

#### 3. **Motor Controller (motor_controller.py)**
- **Servo MG996R** (GPIO 18):
  ```python
  # PWM Control
  LEFT = 2.5    # 0 độ
  CENTER = 7.5  # 90 độ
  RIGHT = 12.5  # 180 độ
  
  pwm.ChangeDutyCycle(LEFT)   # Fresh → Phải
  pwm.ChangeDutyCycle(RIGHT)  # Spoiled → Trái
  ```

- **DC Motor via L298N**:
  ```python
  # GPIO 17: IN1 (Direction 1)
  # GPIO 27: IN2 (Direction 2)
  # GPIO 22: ENA (Speed PWM)
  
  # Forward
  GPIO.output(17, HIGH)
  GPIO.output(27, LOW)
  pwm.ChangeDutyCycle(75)  # 75% speed
  ```

---

### C. **Frontend**

#### 1. **Web Dashboard** (dashboard/)
- **Công nghệ**: HTML, CSS, JavaScript
- **Supabase JS SDK**
- **Features**:
  - Real-time statistics
  - WebSocket updates từ Backend
  - Hardware control panel (Admin only)
  - Image gallery với Supabase Storage

**Real-time Update**:
```javascript
// WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'classification') {
        updateStats(data);
        addToActivity(data);
    }
};

// Supabase realtime
supabase
    .channel('classifications')
    .on('INSERT', (payload) => {
        console.log('New classification:', payload.new);
    })
    .subscribe();
```

#### 2. **Mobile App** (Flutter)
- **Screens**:
  - Dashboard: Stats + Recent classifications
  - History: Grid view với ảnh từ Supabase
  - Settings: Auth, preferences

**Supabase Integration**:
```dart
// Listen to changes
supabase
    .from('classifications')
    .stream(primaryKey: ['id'])
    .order('timestamp', ascending: false)
    .limit(20)
    .listen((data) {
        setState(() {
            classifications = data;
        });
    });
```

---

## 📡 Message Queue (RabbitMQ)

### Queue 1: `fruit_images`
**Producer**: Raspberry Pi  
**Consumer**: Backend Classifier Service

**Message Format**:
```json
{
    "image": "89504e470d0a1a0a0000000d49484452...",
    "metadata": {
        "device_id": "rpi_01",
        "timestamp": 1702345678.5,
        "trigger_mode": "ir_sensor"
    }
}
```

### Queue 2: `classification_results`
**Producer**: Backend Classifier Service  
**Consumer**: Raspberry Pi

**Message Format**:
```json
{
    "classification": "fresh_fruit",
    "confidence": 0.95,
    "processing_time": 0.42,
    "image_url": "https://xxxxx.supabase.co/storage/v1/...",
    "all_probabilities": {
        "fresh_fruit": 0.95,
        "spoiled_fruit": 0.03,
        "other": 0.02
    },
    "image_quality": {
        "brightness": 0.75,
        "sharpness": 0.82,
        "blur": 0.88,
        "contrast": 0.79
    },
    "quality_score": 85.2,
    "recommendation": "✅ Excellent quality | High confidence"
}
```

---

## 🔐 Security & Authentication

### 1. **Supabase Authentication**
```javascript
// Sign in
const { data, error } = await supabase.auth.signInWithPassword({
    email: 'user@example.com',
    password: 'password'
});

// Get session
const { data: { session } } = await supabase.auth.getSession();

// Use in API calls
fetch('/api/admin/endpoint', {
    headers: {
        'Authorization': `Bearer ${session.access_token}`
    }
});
```

### 2. **Row Level Security (RLS)**
```sql
-- Users can only read their own data
CREATE POLICY "Users read own data"
ON users FOR SELECT
USING (auth.uid() = id);

-- Anyone can read classifications
CREATE POLICY "Public read classifications"
ON classifications FOR SELECT
USING (true);

-- Only service role can insert
CREATE POLICY "Service role insert"
ON classifications FOR INSERT
WITH CHECK (true);  -- Checked by service_role key
```

---

## 🚀 Deployment & Scaling

### Local Development
```bash
# Backend
python classifier_service.py
python api.py

# Raspberry Pi
./start.sh

# Dashboard
python -m http.server 3000
```

### Production Considerations

1. **Backend Server**:
   - Deploy lên VPS/Cloud (AWS, GCP, Azure)
   - Use Gunicorn/Uvicorn với multiple workers
   - Add Nginx reverse proxy
   - Enable HTTPS

2. **RabbitMQ**:
   - Standalone installation hoặc CloudAMQP
   - Enable clustering cho high availability
   - Configure persistence

3. **Supabase**:
   - Free tier: 500MB database, 1GB storage
   - Paid: Unlimited scaling
   - Enable connection pooling

4. **Monitoring**:
   - Add logging: ELK Stack, CloudWatch
   - Metrics: Prometheus + Grafana
   - Error tracking: Sentry

---

## 📊 Performance Metrics

| Metric | Target | Actual |
|--------|--------|--------|
| Classification Time | < 1s | ~0.4s |
| End-to-end Latency | < 3s | ~2.5s |
| Throughput | 20/min | 24/min |
| Model Accuracy | > 90% | 92% |
| Image Upload Time | < 2s | ~1.2s |

---

## 🛠️ Troubleshooting

### 1. Pi không gửi được message
```bash
# Check RabbitMQ connection
telnet 192.168.1.100 5672

# Check firewall
# Windows: Open port 5672 in Windows Firewall
```

### 2. Backend không nhận message
```bash
# Check RabbitMQ status
rabbitmqctl status

# Check queue
rabbitmqctl list_queues
```

### 3. Dashboard không cập nhật
```bash
# Check WebSocket connection
# F12 → Network → WS → Check status

# Check Supabase connection
# F12 → Console → Look for errors
```

---

## 📚 Tài Liệu Liên Quan

- [README.md](README.md) - Tổng quan dự án
- [SETUP_GUIDE_VI.md](SETUP_GUIDE_VI.md) - Hướng dẫn cài đặt
- [SUPABASE_SETUP.md](docs/SUPABASE_SETUP.md) - Setup Supabase
- [RABBITMQ_SETUP.md](docs/RABBITMQ_SETUP.md) - Setup RabbitMQ
- [API_REFERENCE.md](docs/API_REFERENCE.md) - API documentation
- [MIGRATION.md](MIGRATION.md) - Firebase → Supabase migration

---

**Tóm tắt**: Hệ thống hoạt động theo mô hình **Event-Driven Architecture** với **Message Queue** làm trung gian, **AI Model** xử lý trên server, **Edge Device** (Pi) chỉ capture và điều khiển hardware, và **Cloud Database** (Supabase) lưu trữ dữ liệu lâu dài.
