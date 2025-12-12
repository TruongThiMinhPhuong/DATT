# Hướng dẫn lắp đặt IR Sensor

## Phần cứng cần thiết

### IR Sensor Module (FC-51 hoặc tương tự)
- **Giá**: 30,000 - 50,000 VND
- **Khoảng cách phát hiện**: 2-30cm (có thể điều chỉnh)
- **Điện áp**: 3.3V - 5V

## Sơ đồ kết nối

```
IR Sensor FC-51          Raspberry Pi 4
┌──────────────┐        ┌──────────────┐
│              │        │              │
│ VCC (5V)     │───────▶│ Pin 2 (5V)   │
│ GND          │───────▶│ Pin 6 (GND)  │
│ OUT          │───────▶│ GPIO 24      │
│              │        │ (Pin 18)     │
└──────────────┘        └──────────────┘
```

### Chi tiết chân kết nối

| IR Sensor Pin | Raspberry Pi Pin | BCM GPIO | Mô tả |
|---------------|------------------|----------|-------|
| VCC           | Pin 2            | -        | Nguồn 5V |
| GND           | Pin 6            | -        | Ground chung |
| OUT           | Pin 18           | GPIO 24  | Tín hiệu phát hiện |

## Lắp đặt phần cứng

### Bước 1: Vị trí lắp đặt
```
                 ┌─────────────┐
                 │   Camera    │
                 └─────────────┘
                       ↓
    ───────────────────────────────────  ← Băng tải
         ↑
    [IR Sensor]  ← Lắp trước camera 10-15cm
```

**Lưu ý:**
- IR sensor đặt **TRƯỚC** camera 10-15cm
- Hướng cảm biến vuông góc với băng tải
- Khoảng cách sensor đến trái cây: 3-10cm

### Bước 2: Điều chỉnh độ nhạy
1. **Xoay biến trở khoảng cách** (Distance potentiometer):
   - Để phát hiện vật thể xa hơn: xoay theo chiều kim đồng hồ
   - Để phát hiện vật thể gần hơn: xoay ngược chiều kim đồng hồ

2. **Test độ nhạy**:
   ```bash
   # Trên Raspberry Pi
   sudo python3 test_ir_sensor.py
   ```

### Bước 3: Kiểm tra kết nối

```bash
# Kiểm tra GPIO
gpio readall

# Hoặc dùng Python
python3 << EOF
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN)
print(f"IR Sensor value: {GPIO.input(24)}")
GPIO.cleanup()
EOF
```

**Hiện tượng:**
- LED trên IR sensor sáng khi phát hiện vật thể
- GPIO 24 = HIGH (1) khi có vật thể
- GPIO 24 = LOW (0) khi không có vật thể

## Cấu hình phần mềm

### File: `config.py`

```python
# Trigger Configuration
TRIGGER_MODE = 'ir_sensor'  # Bật chế độ IR sensor

# IR Sensor Configuration
IR_SENSOR_PIN = 24  # GPIO pin đã kết nối
IR_DEBOUNCE_TIME = 2.0  # Thời gian chống rung (giây)
```

### Điều chỉnh thời gian debounce

**IR_DEBOUNCE_TIME** quyết định thời gian tối thiểu giữa 2 lần phát hiện:

```python
# Băng tải chậm hoặc trái cây lớn
IR_DEBOUNCE_TIME = 3.0  # 3 giây

# Băng tải nhanh hoặc trái cây nhỏ
IR_DEBOUNCE_TIME = 1.5  # 1.5 giây

# Tốc độ trung bình (mặc định)
IR_DEBOUNCE_TIME = 2.0  # 2 giây
```

## Kiểm tra hoạt động

### Test 1: IR Sensor riêng lẻ

Tạo file `test_ir_sensor.py`:

```python
import RPi.GPIO as GPIO
import time

IR_PIN = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

print("Testing IR Sensor on GPIO 24...")
print("Place object in front of sensor...")
print("Press Ctrl+C to exit\n")

try:
    while True:
        if GPIO.input(IR_PIN) == GPIO.HIGH:
            print("✓ Object DETECTED!")
        else:
            print("○ No object")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nTest stopped")
finally:
    GPIO.cleanup()
```

Chạy:
```bash
sudo python3 test_ir_sensor.py
```

### Test 2: Hệ thống hoàn chỉnh

```bash
cd raspberry-pi
sudo python3 main.py
```

**Quan sát log:**
```
IR sensor configured on GPIO 24
Trigger mode: ir_sensor
Conveyor belt started
Fruit detected by IR sensor!
Image sent for classification
Classification: fresh_fruit (confidence: 95.3%)
Sorting CENTER (fresh fruit)
```

## Xử lý sự cố

### IR sensor không phát hiện

**Kiểm tra:**
1. Nguồn điện 5V có đủ không?
2. Dây OUT có kết nối đúng GPIO 24?
3. Biến trở độ nhạy đã điều chỉnh chưa?

**Giải pháp:**
```bash
# Test GPIO
gpio -g mode 24 in
gpio -g read 24  # Nên hiện 0 hoặc 1
```

### Phát hiện liên tục (rung)

**Nguyên nhân:** Debounce time quá ngắn

**Giải pháp:**
```python
# Trong config.py
IR_DEBOUNCE_TIME = 3.0  # Tăng lên 3 giây
```

### LED trên sensor không sáng

**Nguyên nhân:** Không có nguồn hoặc kết nối sai

**Kiểm tra:**
- VCC có kết nối đúng Pin 2 (5V)?
- GND có kết nối đúng Pin 6?
- Sensor có bị hỏng không?

### Phát hiện cách xa/gần bất thường

**Điều chỉnh biến trở:**
- Dùng tua vít nhỏ xoay từ từ
- Test sau mỗi lần điều chỉnh
- Khoảng cách lý tưởng: 5-10cm

## Ưu điểm IR Sensor

✅ **Tiết kiệm tài nguyên**
- Chỉ chụp khi có trái cây
- Giảm 80-90% số ảnh không cần thiết

✅ **Chính xác cao**
- Phát hiện chính xác vị trí trái cây
- Trái cây luôn ở giữa khung hình

✅ **Linh hoạt**
- Không phụ thuộc tốc độ băng tải
- Tự động thích ứng khoảng cách

## Chuyển đổi chế độ

### Dùng IR Sensor (Khuyến nghị)
```python
TRIGGER_MODE = 'ir_sensor'
```

### Dùng Time-based
```python
TRIGGER_MODE = 'time_based'
CAPTURE_INTERVAL = 5.0  # Chụp mỗi 5 giây
```

### Dùng Continuous
```python
TRIGGER_MODE = 'continuous'
```

## Linh kiện khuyến nghị

### IR Sensor modules tốt

1. **FC-51** (Phổ biến nhất)
   - Giá: 30-40k VND
   - Khoảng cách: 2-30cm
   - Dễ điều chỉnh

2. **TCRT5000**
   - Giá: 25-35k VND
   - Khoảng cách: 1-15cm (ngắn hơn)
   - Nhỏ gọn

3. **E18-D80NK**
   - Giá: 60-80k VND
   - Khoảng cách: 3-80cm (xa nhất)
   - Chống nước tốt

**Khuyến nghị:** FC-51 là lựa chọn tốt nhất cho dự án này!
