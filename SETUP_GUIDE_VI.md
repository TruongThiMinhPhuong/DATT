# HƯỚNG DẪN CÀI ĐẶT CHI TIẾT - HỆ THỐNG PHÂN LOẠI HOA QUẢ AI

---

## 📋 MỤC LỤC

1. [Chuẩn Bị Thiết Bị](#1-chuẩn-bị-thiết-bị)
2. [Setup Máy Tính (Laptop/PC)](#2-setup-máy-tính-laptoppc)
3. [Setup Raspberry Pi](#3-setup-raspberry-pi)
4. [Lắp Ráp Phần Cứng](#4-lắp-ráp-phần-cứng)
5. [Kiểm Tra Hệ Thống](#5-kiểm-tra-hệ-thống)
6. [Xử Lý Sự Cố](#6-xử-lý-sự-cố)

---

## 1. CHUẨN BỊ THIẾT BỊ

### 1.1. Danh Sách Thiết Bị Cần Có

#### A. Cho Raspberry Pi ✅

| STT | Thiết Bị | Số Lượng | Ghi Chú |
|-----|----------|----------|---------|
| 1 | Raspberry Pi 4 (8GB RAM) | 1 | Phiên bản 8GB khuyên dùng |
| 2 | Nguồn 5V 3A USB-C | 1 | Chính hãng Raspberry Pi |
| 3 | Thẻ nhớ microSD 32GB+ | 1 | Class 10, A1 trở lên |
| 4 | Camera Module 5MP | 1 | Camera chính hãng Raspberry Pi |
| 5 | Dây ribbon camera | 1 | Đi kèm camera |
| 6 | Servo Motor MG996R | 1 | 180 độ, 11kg.cm |
| 7 | Motor Driver L298N | 1 | Dual H-Bridge |
| 8 | Conveyor Motor JGB37-545 | 1 | 12V DC geared motor |
| 9 | Nguồn 12V 2A | 1 | Cho motor |
| 10 | Cảm biến hồng ngoại | 1 | IR proximity sensor |
| 11 | Breadboard | 1 | 830 holes |
| 12 | Dây jumper | 20+ | Male-Female, Male-Male |
| 13 | Vỏ case Raspberry Pi | 1 | Tùy chọn, bảo vệ Pi |

#### B. Cho Máy Tính (Laptop/PC) ✅

| STT | Yêu Cầu | Thông Số Tối Thiểu |
|-----|---------|-------------------|
| 1 | CPU | Intel i5 hoặc tương đương |
| 2 | RAM | 8GB trở lên |
| 3 | Ổ cứng trống | 10GB+ |
| 4 | Hệ điều hành | Windows 10/11, Ubuntu 20.04+, macOS |
| 5 | Mạng | Cùng WiFi với Raspberry Pi |

#### C. Dụng Cụ Cần Thiết 🔧

- Tua vít Phillips (đầu dẹt +)
- Kìm cắt dây
- Kìm tuốt dây (nếu cần)
- Đồng hồ vạn năng (kiểm tra điện)
- Băng dính điện
- Giấy nhám mịn (tùy chọn)

### 1.2. Kiểm Tra Thiết Bị

**Trước khi bắt đầu, kiểm tra**:

1. ✅ Raspberry Pi không bị hư hỏng
2. ✅ Nguồn 5V 3A hoạt động tốt
3. ✅ Camera không bị trầy, ribbon nguyên vẹn
4. ✅ Motor quay được (thử bằng pin)
5. ✅ L298N không bị cháy IC
6. ✅ Thẻ nhớ format được

---

## 2. SETUP MÁY TÍNH (LAPTOP/PC)

### 2.1. Cài Đặt Python

#### Windows:

**Bước 1**: Tải Python
1. Mở trình duyệt
2. Vào: https://www.python.org/downloads/
3. Click **"Download Python 3.11.x"** (phiên bản mới nhất)
4. Chờ tải về (khoảng 25MB)

**Bước 2**: Cài Đặt Python
1. Mở file vừa tải (python-3.11.x.exe)
2. **QUAN TRỌNG**: ✅ Tích vào **"Add Python to PATH"**
3. Click **"Install Now"**
4. Đợi 2-3 phút
5. Click **"Close"**

**Bước 3**: Kiểm Tra
Mở **Command Prompt** (cmd):
```cmd
python --version
```
Kết quả: `Python 3.11.x` → **Thành công!**

#### Linux/Ubuntu:

Python thường đã có sẵn. Kiểm tra:
```bash
python3 --version
```

Nếu chưa có:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

#### macOS:

```bash
# Cài Homebrew (nếu chưa có)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Cài Python
brew install python@3.11
```

### 2.2. Tải Code Về Máy

**Cách 1: Tải ZIP** (Dễ nhất)

1. Code đã có sẵn tại: `d:\DATT`
2. Bạn đã có đầy đủ file rồi!

**Cách 2: Copy thủ công** (Nếu cần)

Đảm bảo cấu trúc thư mục như sau:
```
d:\DATT\
├── backend\
│   ├── api.py
│   ├── classifier_service.py
│   ├── config.py
│   ├── database.py
│   ├── model.py
│   ├── requirements.txt
│   └── .env.example
├── dashboard\
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── raspberry-pi\
│   ├── main.py
│   ├── camera_module.py
│   ├── motor_controller.py
│   ├── rabbitmq_client.py
│   ├── config.py
│   ├── requirements.txt
│   └── .env.example
├── README.md
└── start-backend.bat
```

### 2.4. Cài Đặt Backend

**Bước 1**: Mở Command Prompt tại thư mục DATT

Cách 1:
- Mở File Explorer
- Vào `d:\DATT`
- Gõ `cmd` vào thanh địa chỉ
- Enter

Cách 2:
```cmd
cd /d d:\DATT
```

**Bước 2**: Tạo Virtual Environment

```cmd
cd backend
python -m venv venv
```
⏳ Đợi 30 giây...

**Bước 3**: Kích hoạt Virtual Environment

```cmd
venv\Scripts\activate
```
Bạn sẽ thấy `(venv)` xuất hiện ở đầu dòng.

**Bước 4**: Cài Dependencies

```cmd
pip install -r requirements.txt
```
⏳ Đợi 3-5 phút (tải TensorFlow, OpenCV...)

**Bước 5**: Tạo File Cấu Hình

```cmd
copy .env.example .env
```

Mở file `.env` bằng Notepad:
```cmd
notepad .env
```

**Không cần sửa gì**, giữ nguyên:
```
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
...
```

Save và đóng.

**Bước 6**: Tạo Thư Mục

```cmd
mkdir models
mkdir data
```

### 2.5. Khởi Động Backend

**Bước 1**: Đảm bảo RabbitMQ đã được cài đặt
- Windows: Cài từ https://www.rabbitmq.com/install-windows.html
- Linux: `sudo apt install rabbitmq-server`
- macOS: `brew install rabbitmq`

**Bước 2**: Quay về thư mục gốc

```cmd
cd ..
```
(Từ `d:\DATT\backend` về `d:\DATT`)

**Bước 3**: Chạy Script Khởi Động

```cmd
start-backend.bat
```

📺 **Bạn sẽ thấy**:
1. Cửa sổ mới 1: **Classifier Service** (màn hình đen với text)
2. Cửa sổ mới 2: **API Server** (màn hình đen với text)
3. Trình duyệt tự động mở Dashboard

**Kiểm tra**:
- RabbitMQ Management: http://localhost:15672
  - User: `guest`
  - Pass: `guest`
- API: http://localhost:8000
- Dashboard: http://localhost:8000/dashboard/

✅ **Nếu thấy Dashboard hiển thị** → Thành công!

### 2.6. Kiểm Tra IP Máy Tính

**Quan trọng**: Raspberry Pi cần IP này để kết nối!

**Windows**:
```cmd
ipconfig
```
Tìm dòng **IPv4 Address** (WiFi hoặc Ethernet):
```
IPv4 Address. . . . . . . . . . . : 192.168.1.100
```
✏️ **Ghi lại IP này**: `192.168.1.100`

**Linux/macOS**:
```bash
ifconfig
# hoặc
ip addr show
```
Tìm `inet 192.168.x.x`

---

## 3. SETUP RASPBERRY PI

### 3.1. Cài Hệ Điều Hành

**Bước 1**: Tải Raspberry Pi Imager

Trên máy tính:
1. Vào: https://www.raspberrypi.com/software/
2. Tải **Raspberry Pi Imager** cho Windows/Mac/Linux
3. Cài đặt Imager

**Bước 2**: Nạp OS vào Thẻ Nhớ

1. Cắm thẻ microSD vào máy tính (dùng adapter)
2. Mở **Raspberry Pi Imager**
3. **Choose OS**: 
   - Raspberry Pi OS (64-bit)
   - **Raspberry Pi OS with desktop** (khuyên dùng)
4. **Choose Storage**: Chọn thẻ SD của bạn
5. **Settings** (biểu tượng bánh răng ⚙️):
   - ✅ Enable SSH
   - ✅ Set username and password:
     - Username: `pi`
     - Password: `raspberry` (hoặc tự đặt)
   - ✅ Configure WiFi:
     - SSID: (tên WiFi nhà bạn)
     - Password: (mật khẩu WiFi)
     - Country: `VN`
   - ✅ Set timezone: `Asia/Ho_Chi_Minh`
6. Click **SAVE**
7. Click **WRITE**
8. Đợi 10-15 phút...

**Bước 3**: Khởi động Raspberry Pi

1. Rút thẻ SD ra khỏi máy tính
2. Cắm thẻ SD vào Raspberry Pi
3. Cắm nguồn 5V 3A vào Pi
4. Đèn LED đỏ sáng, đèn xanh nhấp nháy → **Đang boot**
5. Đợi 2-3 phút lần đầu

**Bước 4**: Kết nối SSH

Từ máy tính, mở Command Prompt:

**Cách 1: Dùng hostname**
```cmd
ssh pi@raspberrypi.local
```

**Cách 2: Dùng IP**
Nếu cách 1 không được, tìm IP của Pi:
- Vào router admin panel
- Hoặc dùng app "Fing" trên điện thoại
- Tìm device tên "raspberry"

```cmd
ssh pi@192.168.1.50
```
(Thay `192.168.1.50` bằng IP thực của Pi)

Lần đầu sẽ hỏi:
```
Are you sure you want to continue connecting (yes/no)?
```
Gõ `yes` → Enter

Nhập password: `raspberry` (hoặc password bạn đã đặt)

✅ **Thấy dòng chữ `pi@raspberrypi:~ $`** → Đã SSH thành công!

### 3.2. Cấu Hình Raspberry Pi

**Trong SSH Terminal**:

**Bước 1**: Update hệ thống
```bash
sudo apt update
sudo apt upgrade -y
```
⏳ Đợi 5-10 phút...

**Bước 2**: Cài Đặt Dependencies
```bash
sudo apt install -y python3-pip python3-venv libcap-dev git
```

**Bước 3**: Enable Camera
```bash
sudo raspi-config
```
Màn hình menu xuất hiện:
1. Dùng mũi tên ↓ chọn **"Interface Options"** → Enter
2. Chọn **"Camera"** → Enter
3. Chọn **"Yes"** → Enter
4. Chọn **"OK"** → Enter
5. Chọn **"Finish"** → Enter
6. Reboot khi được hỏi: **"Yes"**

```bash
sudo reboot
```

Đợi 1 phút, SSH lại vào Pi.

**Bước 4**: Kiểm Tra Camera
```bash
vcgencmd get_camera
```
Kết quả: `supported=1 detected=1` → **Camera OK!**

### 3.3. Tải Code Lên Raspberry Pi

**Cách 1: Dùng Git** (Khuyên dùng)

**Trên Pi** (qua SSH):
```bash
cd ~
mkdir projects
cd projects
```

**Từ máy tính**, copy folder `raspberry-pi`:

**Windows** (PowerShell):
```powershell
scp -r d:\DATT\raspberry-pi pi@raspberrypi.local:~/projects/
```

Hoặc dùng **WinSCP** (GUI):
1. Tải WinSCP: https://winscp.net/
2. Kết nối:
   - Host: `raspberrypi.local`
   - User: `pi`
   - Password: `raspberry`
3. Drag & drop folder `raspberry-pi` từ `d:\DATT` sang `/home/pi/projects/`

**Cách 2: Tạo File Thủ Công**

```bash
cd ~
mkdir -p projects/raspberry-pi
cd projects/raspberry-pi
```

Tạo từng file bằng `nano`:
```bash
nano config.py
```
Copy nội dung từ máy tính, paste vào.
Lưu: `Ctrl+O` → Enter → `Ctrl+X`

Làm tương tự cho tất cả file.

### 3.4. Cài Đặt Python Dependencies

```bash
cd ~/projects/raspberry-pi
```

**Bước 1**: Tạo Virtual Environment
```bash
python3 -m venv venv
```

**Bước 2**: Activate
```bash
source venv/bin/activate
```
Thấy `(venv)` ở đầu dòng.

**Bước 3**: Upgrade pip
```bash
pip install --upgrade pip
```

**Bước 4**: Cài Dependencies
```bash
pip install -r requirements.txt
```
⏳ Đợi 10-15 phút (picamera2, opencv lâu)

**Lưu ý**: Nếu lỗi picamera2:
```bash
sudo apt install -y python3-picamera2
```

### 3.5. Cấu Hình Kết Nối Backend

**Bước 1**: Tạo file .env
```bash
cp .env.example .env
nano .env
```

**Bước 2**: Sửa IP máy tính
```bash
RABBITMQ_HOST=192.168.1.100  # ← Thay bằng IP máy tính của bạn
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
```

Lưu: `Ctrl+O` → Enter → `Ctrl+X`

**Bước 3**: Test kết nối
```bash
ping 192.168.1.100
```
Thấy reply → **OK!**
`Ctrl+C` để dừng.

### 3.6. Test Raspberry Pi Code

**Test Camera**:
```bash
python camera_module.py
```
Nếu OK, sẽ tạo file `test_capture.jpg`

Xem ảnh:
```bash
ls -lh test_capture.jpg
```

**Test Motor** (CHƯA NỐI MOTOR):
```bash
# Sẽ test sau khi nối dây
```

---

## 4. LẮP RÁP PHẦN CỨNG

### 4.1. Chuẩn Bị

**⚠️ AN TOÀN**:
- Ngắt nguồn tất cả thiết bị
- Không nối nguồn khi đang nối dây
- Kiểm tra cực +/- trước khi cấp điện

### 4.2. Sơ Đồ Tổng Quan

```
                    [Nguồn 5V 3A]
                          |
                    [Raspberry Pi 4]
                          |
        +-----------------+-----------------+
        |                 |                 |
    [Camera]          [Servo]           [L298N]
                                            |
                                      [Conveyor]
                                            |
                                      [Nguồn 12V]
```

### 4.3. Nối Camera Module

**Bước 1**: Tắt Raspberry Pi (rút nguồn)

**Bước 2**: Tìm CSI Port
- Cổng camera nằm giữa HDMI và jack audio
- Có nắp đen nhựa

**Bước 3**: Mở Nắp
- Nhẹ nhàng kéo nắp đen **lên trên**
- Đừng kéo ra ngoài!

**Bước 4**: Cắm Ribbon Cable
- Dây ribbon màu xanh (hoặc trắng)
- **Mặt xanh (contacts) quay vào jack audio**
- **Mặt xanh quay ra ngoài HDMI**
- Đẩy nhẹ vào đến cùng

**Bước 5**: Đóng Nắp
- Ấn nắp đen xuống chặt

**Kiểm tra**:
```
[Raspberry Pi]
      |
      |  [CSI Port]
      |    |
      |    | (Ribbon cable - contacts vào phía jack audio)
      |    |
  [Camera Module]
```

### 4.4. Nối Servo Motor MG996R

**Thông Số Servo**:
- Dây Cam/Vàng: **Signal** (GPIO 18)
- Dây Đỏ: **5V Power**
- Dây Nâu/Đen: **Ground**

**Sơ Đồ Nối**:

```
Servo Motor          Raspberry Pi
┌─────────┐         ┌──────────┐
│ MG996R  │         │   GPIO   │
└─┬──┬──┬─┘         └──────────┘
  │  │  │
  │  │  └─ Nâu ──→  Pin 6  (Ground)
  │  └──── Đỏ  ──→  Pin 2  (5V)
  └─────── Cam ──→  Pin 12 (GPIO 18)
```

**Bảng Pin Raspberry Pi** (BCM mode):

| Pin Vật Lý | Tên | Kết Nối |
|------------|-----|---------|
| Pin 2 | 5V | Servo Đỏ |
| Pin 6 | GND | Servo Nâu |
| Pin 12 | GPIO 18 | Servo Cam |

**Cách Nối**:
1. Dùng dây jumper **Male-Female**
2. Servo (Male) → Jumper (Female) → Raspberry Pi (Male pins)

**Lưu ý**:
- Servo quay mạnh, nếu dùng nhiều servo → **Nguồn ngoài 5V**
- Với 1 servo nhỏ, 5V từ Pi OK

### 4.5. Nối L298N Motor Driver

**Sơ Đồ L298N**:

```
      [L298N Motor Driver]
      
+12V  GND  5V  ENA  IN1  IN2  IN3  IN4  ENB
 |     |    |    |    |    |    |    |    |
 |     |    X    |    |    |    X    X    X
 |     |         |    |    |
 |     |         |    |    |
12V   12V       Pi   Pi   Pi
Nguồn  GND     Pin11 Pin13 Pin15
```

**Chi Tiết**:

| L298N | Kết Nối | Ghi Chú |
|-------|---------|---------|
| **12V** | Nguồn 12V (+) | Cực dương nguồn motor |
| **GND** | Nguồn 12V (-) **VÀ** Pi GND | **CHUNG MASS** |
| **5V** | **KHÔNG NỐI** | Tháo jumper nếu có |
| **ENA** | GPIO 17 (Pin 11) | PWM speed control |
| **IN1** | GPIO 27 (Pin 13) | Direction 1 |
| **IN2** | GPIO 22 (Pin 15) | Direction 2 |
| **OUT1** | Conveyor Motor (+) | Motor cực dương |
| **OUT2** | Conveyor Motor (-) | Motor cực âm |

**Bảng GPIO**:

| Pin Vật Lý | GPIO BCM | Tên | Nối L298N |
|------------|----------|-----|-----------|
| Pin 6 | GND | Ground | GND (chung với 12V) |
| Pin 11 | GPIO 17 | ENA | ENA |
| Pin 13 | GPIO 27 | IN1 | IN1 |
| Pin 15 | GPIO 22 | IN2 | IN2 |

**⚠️ QUAN TRỌNG**:
- **CHUNG MASS**: GND của Raspberry Pi **PHẢI NỐI** GND của nguồn 12V
- Nếu không chung mass → Motor không hoạt động hoặc Raspberry Pi hỏng!

### 4.6. Nối IR Sensor (Cảm Biến Phát Hiện)

**Sensor có 3 chân**:
- **VCC**: Nguồn 5V
- **GND**: Ground
- **OUT**: Output signal

**Sơ Đồ**:

```
IR Sensor            Raspberry Pi
┌─────────┐         ┌──────────┐
│  ┌───┐  │         │          │
│  │ · │  │         │          │
│  └───┘  │         │          │
└─┬──┬──┬─┘         └──────────┘
  │  │  │
VCC GND OUT
  │  │  │
  │  │  └─────→ Pin 16 (GPIO 23)
  │  └────────→ Pin 6  (GND)
  └───────────→ Pin 2  (5V)
```

### 4.7. Sơ Đồ Hoàn Chỉnh

```
╔══════════════════════════════════════════════════════════════╗
║                    RASPBERRY PI 4 GPIO                        ║
╠══════════════════════════════════════════════════════════════╣
║  Pin 2  (5V)    ──→ Servo Đỏ, IR VCC                        ║
║  Pin 6  (GND)   ──→ Servo Nâu, IR GND, L298N GND            ║
║  Pin 11 (G17)   ──→ L298N ENA                                ║
║  Pin 12 (G18)   ──→ Servo Cam (Signal)                       ║
║  Pin 13 (G27)   ──→ L298N IN1                                ║
║  Pin 15 (G22)   ──→ L298N IN2                                ║
║  Pin 16 (G23)   ──→ IR Sensor OUT                            ║
╚══════════════════════════════════════════════════════════════╝
                          ↓
                  ┌───────────────┐
                  │   L298N       │
                  ├───────────────┤
                  │ 12V ← 12V Src │
                  │ GND ← 12V GND │
                  │ OUT1/2 → Motor│
                  └───────────────┘
                          ↓
                  ┌───────────────┐
                  │ Conveyor Motor│
                  │   JGB37-545   │
                  └───────────────┘
```

### 4.8. Lắp Breadboard (Tùy Chọn)

Nếu dùng breadboard để dễ quản lý:

```
    Breadboard
    ==========
5V  ─┬─┬─┬─┬─  5V Rail
     │ │ │ │
GND ─┼─┼─┼─┼─  GND Rail
     │ │ │ │
     Servo  IR  L298N  ...
```

### 4.9. Checklist Nối Dây

Trước khi bật nguồn, kiểm tra:

- [ ] Camera ribbon cắm đúng hướng
- [ ] Servo nối đúng: Cam→GPIO18, Đỏ→5V, Nâu→GND
- [ ] L298N chung GND với Raspberry Pi
- [ ] L298N: IN1→G27, IN2→G22, ENA→G17
- [ ] IR Sensor: VCC→5V, GND→GND, OUT→G23
- [ ] Conveyor motor nối OUT1, OUT2 của L298N
- [ ] Nguồn 12V nối 12V và GND của L298N
- [ ] **KHÔNG nối L298N 5V** ra Raspberry Pi
- [ ] Tất cả dây cắm chắc chắn
- [ ] Không có dây nào chạm mass ngắn mạch

---

## 5. KIỂM TRA HỆ THỐNG

### 5.1. Test Phần Cứng Raspberry Pi

**Bước 1**: Boot Raspberry Pi
```bash
# Cắm nguồn 5V cho Pi
# SSH vào Pi
ssh pi@raspberrypi.local
```

**Bước 2**: Test Camera
```bash
cd ~/projects/raspberry-pi
source venv/bin/activate
python camera_module.py
```

Kết quả:
```
Testing Camera Module...
Camera initialized successfully
Captured image: XXXXX bytes
Test image saved as test_capture.jpg
```

✅ **Thành công!**

**Bước 3**: Test Motor Controller

**⚠️ QUAN TRỌNG**: Chưa nối motor thật!

```bash
python motor_controller.py
```

Sẽ test servo và conveyor:
- Servo: Left → Center → Right → Center
- Conveyor: Start → Stop

**Quan sát**:
- Servo quay 3 vị trí
- Nếu nối motor: Conveyor quay 3 giây → Dừng

❌ **Nếu có lỗi**:
```
RuntimeError: Cannot determine SOC peripheral base address
```
→ Bạn đang chạy trên máy tính, không phải Pi!

✅ **Thành công khi không báo lỗi!**

### 5.2. Test Kết Nối Backend

**Trên Máy Tính**:
- Đảm bảo Backend đang chạy (`start-backend.bat`)
- RabbitMQ Management mở được: http://localhost:15672

**Trên Raspberry Pi**:

**Bước 1**: Test ping
```bash
ping 192.168.1.100
```
(Thay IP máy tính của bạn)

Thấy reply → OK! `Ctrl+C` dừng.

**Bước 2**: Test RabbitMQ connection
```bash
python rabbitmq_client.py
```

Kết quả mong đợi:
```
Testing RabbitMQ Client...
Connected successfully
Started consuming classification results
Test message sent
```

Nếu lỗi kết nối:
- Kiểm tra IP trong `.env`
- Kiểm tra firewall Windows (tắt tạm)
- Kiểm tra RabbitMQ đang chạy

### 5.3. Test Toàn Hệ Thống

**Bước 1**: Đảm bảo tất cả đang chạy

**Trên Máy Tính**:
✅ RabbitMQ running
✅ Classifier Service window open
✅ API Server window open
✅ Dashboard: http://localhost:8000/dashboard/

**Bước 2**: Chạy Main App trên Pi

```bash
cd ~/projects/raspberry-pi
source venv/bin/activate
python main.py
```

Kết quả:
```
=== Initializing Fruit Sorting System ===
✅ Camera initialized successfully
✅ Motor controller initialized
✅ RabbitMQ connected
=== System Initialized Successfully ===
=== Starting Fruit Sorting System ===
Conveyor belt started
```

**Bước 3**: Kiểm Tra Dashboard

Mở Dashboard: http://localhost:8000/dashboard/

Bạn thấy:
- Status: **Connected** (màu xanh)
- Statistics: Đang 0 (chưa có data)

**Bước 4**: Test Với Vật Thật

1. **Đặt hoa quả** (hoặc vật bất kỳ) trước IR sensor
2. **Quan sát**:
   - Pi: "Fruit detected!"
   - Pi: "Image sent for classification"
   - Backend: Nhận ảnh, xử lý
   - Pi: Nhận kết quả
   - Servo: Quay theo kết quả
   - Dashboard: Cập nhật thống kê

✅ **Hệ thống hoạt động!**

---

## 6. XỬ LÝ SỰ CỐ

### 6.1. Raspberry Pi Không Boot

**Triệu chứng**: Đèn đỏ sáng, đèn xanh không nháy

**Nguyên nhân**:
- Thẻ SD lỗi
- Nguồn không đủ

**Giải pháp**:
1. Thử nguồn khác 5V 3A
2. Ghi lại OS vào thẻ SD
3. Thử thẻ SD khác

### 6.2. Camera Không Hoạt Động

**Lỗi**: `Camera not detected`

**Giải pháp**:
```bash
# Kiểm tra camera
vcgencmd get_camera

# Nếu detected=0
sudo raspi-config
# → Interface → Camera → Enable
sudo reboot
```

**Ribbon cable lỏng**: Mở và cắm lại

### 6.3. Motor Không Quay

**Servo không quay**:
- Kiểm tra dây nối đúng chân
- Test bằng code đơn giản:
```python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
pwm = GPIO.PWM(18, 50)
pwm.start(7.5)  # Center
time.sleep(2)
pwm.stop()
GPIO.cleanup()
```

**Conveyor không quay**:
- Kiểm tra chung GND
- Kiểm tra nguồn 12V
- Test motor bằng pin trực tiếp
- Kiểm tra L298N không bị hỏng

### 6.4. Không Kết Nối RabbitMQ

**Lỗi**: `Connection refused`

**Từ Raspberry Pi**:
```bash
# Test kết nối
telnet 192.168.1.100 5672
```

Nếu không kết nối được:

**Windows**:
1. Mở **Windows Defender Firewall**
2. **Advanced Settings**
3. **Inbound Rules** → **New Rule**
4. Port → **5672** → Allow
5. Áp dụng cho Domain, Private, Public

Hoặc tắt firewall tạm:
```cmd
# Run as Admin
netsh advfirewall set allprofiles state off
```

### 6.5. TensorFlow Import Lỗi

**Trên Pi**:
TensorFlow nặng, có thể lỗi trên Pi. Backend chạy trên máy tính nên OK.

**Trên Máy Tính**:
```cmd
pip install tensorflow==2.15.0
```

Nếu lỗi, thử:
```cmd
pip install tensorflow-cpu==2.15.0
```

### 6.6. Dashboard Không Hiển Thị

**Kiểm tra**:
1. API có chạy? http://localhost:8000
2. Console F12 có lỗi?
3. WebSocket connected?

**Fix**:
```cmd
# Restart backend
taskkill /F /FI "WINDOWTITLE eq API Server"
taskkill /F /FI "WINDOWTITLE eq Classifier Service"
start-backend.bat
```

### 6.7. Quality Metrics Không Cập Nhật

Đảm bảo đã:
1. Cài `opencv-python` trong backend
2. Restart classifier service
3. Gửi ảnh mới

---

## 7. TIPS & TRICKS

### 7.1. Tối Ưu Hóa

**Cải thiện độ chính xác**:
1. Ánh sáng tốt (đều, không quá sáng/tối)
2. Camera ổn định, không rung
3. Khoảng cách tối ưu: 20-30cm
4. Nền đơn giản, tương phản cao

**Tăng tốc độ**:
1. Giảm camera resolution (nếu cần)
2. Tăng tốc conveyor
3. Giảm `CAPTURE_DELAY` trong config

### 7.2. Bảo Trì

**Định kỳ**:
- Vệ sinh camera lens
- Kiểm tra dây nối
- Bôi trơn motor
- Backup code và database

### 7.3. Mở Rộng

**Thêm tính năng**:
- Thêm loại hoa quả (sửa `config.MODEL_CLASSES`)
- Email alerts khi lỗi
- Log ra file
- Tích hợp cloud storage
- Mobile app

---

## 8. KẾT LUẬN

### 8.1. Checklist Hoàn Thành

- [ ] Máy tính: Python và RabbitMQ cài đặt
- [ ] Máy tính: Backend chạy thành công
- [ ] Raspberry Pi: OS cài đặt, SSH được
- [ ] Raspberry Pi: Camera hoạt động
- [ ] Raspberry Pi: Code cài đặt
- [ ] Phần cứng: Camera nối đúng
- [ ] Phần cứng: Servo hoạt động
- [ ] Phần cứng: Conveyor hoạt động
- [ ] Phần cứng: IR sensor phát hiện
- [ ] Kết nối: Pi ↔ Backend OK
- [ ] Test: Toàn hệ thống hoạt động
- [ ] Dashboard: Hiển thị real-time

### 8.2. Tài Liệu Tham Khảo

- **Main README**: [README.md](file:///d:/DATT/README.md)
- **Hardware Guide**: [HARDWARE_SETUP.md](file:///d:/DATT/HARDWARE_SETUP.md)
- **Upgrades**: [UPGRADES.md](file:///C:/Users/minhp/.gemini/antigravity/brain/25d06ba0-3a06-4dee-917b-471a13aa2b80/UPGRADES.md)
- **Walkthrough**: [walkthrough.md](file:///C:/Users/minhp/.gemini/antigravity/brain/25d06ba0-3a06-4dee-917b-471a13aa2b80/walkthrough.md)

### 8.3. Hỗ Trợ

**Nếu gặp vấn đề**:
1. Đọc lại hướng dẫn từng bước
2. Kiểm tra [Xử Lý Sự Cố](#6-xử-lý-sự-cố)
3. Xem log trong terminal
4. Kiểm tra Dashboard recommendations

**Resources**:
- Raspberry Pi Documentation: https://www.raspberrypi.com/documentation/
- TensorFlow Tutorials: https://www.tensorflow.org/tutorials
- FastAPI Docs: https://fastapi.tiangolo.com/

---

**CHÚC BẠN THÀNH CÔNG! 🚀🍎🤖**
