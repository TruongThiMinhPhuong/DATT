#!/usr/bin/env python3
"""
Hướng Dẫn Phần Cứng và Sơ Đồ Kết Nối
Hệ Thống Phân Loại Trái Cây với LM2596 Buck Converter
"""

print("="*60)
print("🍓 HỆ THỐNG PHÂN LOẠI TRÁI CÂY AI - THIẾT LẬP PHẦN CỨNG")
print("="*60)

print("""
🔧 CÁC THÀNH PHẦN PHẦN CỨNG:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 🖥️  Bộ Điều Khiển Chính:
   • Raspberry Pi 4 (khuyến nghị 4GB/8GB)
   • Thẻ MicroSD 32GB+ (Class 10)
   • Tản nhiệt + Quạt làm mát

2. 📷 Hệ Thống Camera:
   • Raspberry Pi Camera Module 5MP
   • Cáp camera (15-pin đến 22-pin)
   • Giá đỡ camera

3. 🔄 Hệ Thống Động Cơ:
   • Servo Motor MG996R (6V, mô-men xoắn 15kg⋅cm)
   • DC Gear Motor JGB37-545 (12V)
   • Module Driver Motor L298N

4. 🔍 Cảm Biến:
   • Cảm Biến IR Tránh Vật Cản FC-51
   • Dây nối jumper (Male-Female, Male-Male)

5. ⚡ Hệ Thống Nguồn Điện:
   • Adapter Nguồn 12V 5A (Nguồn Chính)
   • Module LM2596 Buck Converter (12V→6V cho servo)
   • Board phân phối nguồn
   • Tụ điện: 1000µF/16V (ổn định nguồn servo)

6. 🔗 Kết Nối:
   • Breadboard hoặc board mạch in thử nghiệm
   • Cực nối terminal
   • Ống co nhiệt
   • Kẹp quản lý cáp

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ KIẾN TRÚC HỆ THỐNG NGUỒN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Nguồn Chính (12V/5A)
├── Raspberry Pi 4 ←── Adapter USB-C 5V/3A
├── LM2596 Buck Converter (12V → 6V/3A)
│   └── Servo Motor MG996R (6V)
├── L298N Motor Driver (12V)
│   └── Motor Băng Tải JGB37-545 (12V)
└── Cảm Biến IR ←── 5V từ Pi GPIO

🔧 THIẾT LẬP LM2596:
• Đầu vào: 12V từ nguồn chính
• Đầu ra: 6V (điều chỉnh bằng biến trở)
• Giới hạn dòng: Tối đa 3A
• Thêm tụ 1000µF ở đầu ra để ổn định servo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔌 SƠ ĐỒ KẾT NỐI GPIO (Raspberry Pi 4):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Sơ Đồ Pin (Pin vật lý bên trái, BCM GPIO bên phải):
┌─────────────────────────────────────────┐
│   Pin Vật Lý  │ BCM GPIO │ Thành Phần   │
├─────────────────────────────────────────┤
│       2       │   5V     │ Cảm Biến IR  │
│       4       │   5V     │ Dự phòng     │
│       6       │   GND    │ GND Chung    │
│      12       │  GPIO18  │ Servo PWM    │
│      11       │  GPIO17  │ L298N ENA    │
│      13       │  GPIO27  │ L298N IN1    │
│      15       │  GPIO22  │ L298N IN2    │
│      16       │  GPIO23  │ Dừng Khẩn*   │
│      18       │  GPIO24  │ Cảm Biến IR  │
│      20       │   GND    │ Cảm Biến IR  │
└─────────────────────────────────────────┘
*Dừng Khẩn Cấp (Tùy chọn)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 KẾT NỐI CHI TIẾT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 SERVO MG996R (qua LM2596):
   • Dây Đỏ     → LM2596 Đầu Ra (+6V)
   • Dây Nâu    → LM2596 GND
   • Dây Cam    → Pi GPIO 18 (PWM)

📍 LM2596 BUCK CONVERTER:
   • VIN+  → Nguồn Chính +12V
   • VIN-  → Nguồn Chính GND
   • VOUT+ → Dây Đỏ Servo (+6V)
   • VOUT- → Dây Nâu Servo & Pi GND
   • Biến trở: Điều chỉnh chính xác 6.0V

📍 L298N MOTOR DRIVER:
   • VCC  → Nguồn Chính +12V
   • GND  → Nguồn Chính GND
   • ENA  → Pi GPIO 17
   • IN1  → Pi GPIO 27
   • IN2  → Pi GPIO 22
   • OUT1 → Motor Băng Tải (+)
   • OUT2 → Motor Băng Tải (-)

📍 CẢM BIẾN IR FC-51:
   • VCC → Pi Pin 2 (+5V)
   • GND → Pi Pin 6 (GND)
   • OUT → Pi GPIO 24

📍 MODULE CAMERA:
   • Kết nối qua cổng camera 15-pin
   • Kích hoạt bằng: sudo raspi-config

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 MẸO LẮP RÁP:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 📏 Hiệu Chuẩn LM2596:
   • Dùng đồng hồ vạn năng đặt đầu ra chính xác 6.0V
   • Kiểm tra với servo kết nối (kiểm tra có tải)
   • Thêm tụ điện gần servo để giảm nhiễu

2. 🔒 Biện Pháp An Toàn:
   • Sử dụng cầu chì: 1A cho Pi, 2A cho servo, 5A cho băng tải
   • Thêm đèn LED báo trạng thái nguồn
   • Nối đất đúng cách - cấu hình star ground

3. 📦 Lắp Đặt:
   • Cố định tất cả linh kiện lên đế
   • Dùng standoff cho Pi và các module
   • Quản lý cáp gọn gàng

4. 🌡️  Quản Lý Nhiệt:
   • LM2596 có thể cần tản nhiệt khi hoạt động
   • Thông gió đầy đủ cho Pi
   • Giữ linh kiện tránh xa nguồn nhiệt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  LƯU Ý QUAN TRỌNG:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• TUYỆT ĐỐI không nối servo trực tiếp vào 12V (sẽ hỏng!)
• Luôn hiệu chuẩn LM2596 trước khi nối servo
• Kiểm tra từng linh kiện riêng biệt trước khi lắp hoàn chỉnh
• Dùng dây đúng chuẩn: 18AWG cho motor, 22AWG cho tín hiệu
• Kiểm tra kỹ cực tính trước khi cấp nguồn

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

print("🎯 Hệ thống sẵn sàng kiểm tra!")
print("Chạy lệnh: python3 test_hardware.py")
print("="*60)