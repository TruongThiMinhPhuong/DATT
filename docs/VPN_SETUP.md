# 🌐 Setup Mạng VPN - ZeroTier / Tailscale

Hướng dẫn setup VPN để giữ IP cố định, kết nối ổn định từ xa.

---

## 🎯 Tại sao cần VPN?

### ❌ Vấn đề với IP thông thường:
- IP thay đổi khi đổi mạng WiFi
- Không kết nối được từ xa (khác mạng LAN)
- Phải config lại mỗi khi đổi network
- Không bảo mật khi đi qua Internet

### ✅ Lợi ích khi dùng VPN:
- ✅ **IP cố định** - Không bao giờ thay đổi
- ✅ **Kết nối từ xa** - Ở bất cứ đâu có Internet
- ✅ **Bảo mật** - Mã hóa end-to-end
- ✅ **Đơn giản** - Setup 1 lần, dùng mãi mãi

---

## 🆚 So sánh ZeroTier vs Tailscale

| Tính năng | ZeroTier | Tailscale |
|-----------|----------|-----------|
| **Miễn phí** | 25 devices | 20 devices |
| **Tốc độ** | Nhanh | Rất nhanh (WireGuard) |
| **Dễ setup** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **UI** | Web-based | Web + CLI tốt |
| **Đề xuất** | Cơ bản, đơn giản | **KHUYẾN NGHỊ** |

**Khuyến nghị: Dùng Tailscale** - Dễ hơn, nhanh hơn, UI tốt hơn.

---

## 🚀 OPTION 1: TAILSCALE (Khuyến nghị)

### Bước 1: Tạo tài khoản

1. Truy cập: https://tailscale.com
2. Click **"Get started"**
3. Đăng nhập bằng Google/GitHub/Email
4. Tài khoản miễn phí - 20 devices

### Bước 2: Install trên Backend (Laptop)

**Windows:**
```bash
# Download từ: https://tailscale.com/download/windows
# Chạy installer
# Sau khi cài xong, click "Connect" và đăng nhập
```

**Linux:**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

**macOS:**
```bash
brew install tailscale
sudo tailscale up
```

### Bước 3: Install trên Raspberry Pi

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Kết nối (sẽ hiện link để đăng nhập)
sudo tailscale up

# Copy link và mở trên browser để xác thực
```

### Bước 4: Lấy IP Tailscale

**Trên Laptop:**
```bash
# Xem IP Tailscale của laptop
tailscale ip -4

# Ví dụ output: 100.64.1.2
```

**Trên Raspberry Pi:**
```bash
# Xem IP Tailscale của Pi
sudo tailscale ip -4

# Ví dụ output: 100.64.1.3
```

### Bước 5: Cấu hình hệ thống

**Sửa `raspberry-pi/config.py`:**
```python
# Dùng IP Tailscale của laptop thay vì IP LAN
RABBITMQ_HOST = '100.64.1.2'  # ← IP Tailscale của laptop
```

**Hoặc dùng `.env`:**
```env
RABBITMQ_HOST=100.64.1.2
```

### Bước 6: Test kết nối

**Từ Raspberry Pi, ping laptop:**
```bash
ping 100.64.1.2  # IP Tailscale của laptop
```

**Nếu ping được → Thành công!** ✅

### Bước 7: Chạy hệ thống

```bash
# Trên Laptop - Backend
cd backend
python classifier_service.py  # Terminal 1
python api.py                 # Terminal 2

# Trên Raspberry Pi
cd raspberry-pi
./start.sh
```

---

## 🔷 OPTION 2: ZEROTIER

### Bước 1: Tạo tài khoản & Network

1. Truy cập: https://my.zerotier.com
2. Đăng ký tài khoản miễn phí
3. Click **"Create A Network"**
4. Copy **Network ID** (16 ký tự hex)
   - Ví dụ: `a0cbf4b62a1234567`

### Bước 2: Install trên Backend (Laptop)

**Windows:**
```bash
# Download từ: https://www.zerotier.com/download/
# Chạy installer
# Join network:
# - Mở ZeroTier tray icon
# - Click "Join Network"
# - Nhập Network ID
```

**Linux:**
```bash
curl -s https://install.zerotier.com | sudo bash
sudo zerotier-cli join a0cbf4b62a1234567  # Thay Network ID
```

**macOS:**
```bash
# Download từ: https://www.zerotier.com/download/
# Sau khi cài:
sudo zerotier-cli join a0cbf4b62a1234567
```

### Bước 3: Install trên Raspberry Pi

```bash
# Install ZeroTier
curl -s https://install.zerotier.com | sudo bash

# Join network
sudo zerotier-cli join a0cbf4b62a1234567  # Thay Network ID của bạn
```

### Bước 4: Authorize devices

1. Quay lại https://my.zerotier.com
2. Click vào network vừa tạo
3. Scroll xuống **"Members"**
4. Tích ✅ vào checkbox **"Auth?"** cho cả 2 devices
5. Xem IP được gán (cột "Managed IPs")
   - Laptop: VD `10.147.20.1`
   - Raspberry Pi: VD `10.147.20.2`

### Bước 5: Cấu hình hệ thống

**Sửa `raspberry-pi/config.py`:**
```python
# Dùng IP ZeroTier của laptop
RABBITMQ_HOST = '10.147.20.1'  # ← IP ZeroTier của laptop
```

### Bước 6: Test kết nối

```bash
# Từ Pi, ping laptop
ping 10.147.20.1
```

---

## 🎯 Update Config Files

### File 1: `raspberry-pi/config.py`

**Trước:**
```python
RABBITMQ_HOST = '192.168.1.100'  # IP LAN - thay đổi
```

**Sau (Tailscale):**
```python
RABBITMQ_HOST = '100.64.1.2'  # IP Tailscale - CỐ ĐỊNH
```

**Sau (ZeroTier):**
```python
RABBITMQ_HOST = '10.147.20.1'  # IP ZeroTier - CỐ ĐỊNH
```

### File 2: `raspberry-pi/.env`

```env
RABBITMQ_HOST=100.64.1.2  # Tailscale
# hoặc
RABBITMQ_HOST=10.147.20.1  # ZeroTier
```

### File 3: `backend/hardware_api.py`

**Dòng 16 - Sửa Raspberry Pi host:**
```python
# Trước
RASPBERRY_PI_HOST = "http://raspberrypi.local:5000"

# Sau (Tailscale)
RASPBERRY_PI_HOST = "http://100.64.1.3:5000"  # IP Tailscale của Pi

# Sau (ZeroTier)
RASPBERRY_PI_HOST = "http://10.147.20.2:5000"  # IP ZeroTier của Pi
```

---

## 📱 Mobile App Config

**File: `mobile_app/lib/services/api_service.dart`**

```dart
// Dòng 6 - Sửa backend URL
ApiService({this.baseUrl = 'http://100.64.1.2:8000'});  // Tailscale
// hoặc
ApiService({this.baseUrl = 'http://10.147.20.1:8000'});  // ZeroTier
```

---

## ✅ Checklist Setup

### Tailscale (Khuyến nghị)
- [ ] Tạo tài khoản tại tailscale.com
- [ ] Install trên Laptop
- [ ] Install trên Raspberry Pi
- [ ] Lấy IP: `tailscale ip -4`
- [ ] Update `config.py` với IP Tailscale
- [ ] Update `hardware_api.py`
- [ ] Test: `ping <IP>`
- [ ] Chạy hệ thống

### ZeroTier
- [ ] Tạo tài khoản tại my.zerotier.com
- [ ] Tạo Network, copy Network ID
- [ ] Install trên Laptop
- [ ] Install trên Raspberry Pi
- [ ] Join network cả 2 máy
- [ ] Authorize trên web dashboard
- [ ] Lấy IP từ web dashboard
- [ ] Update config files
- [ ] Test: `ping <IP>`
- [ ] Chạy hệ thống

---

## 🔧 Commands Hữu ích

### Tailscale

```bash
# Xem IP
tailscale ip

# Xem status
tailscale status

# Xem tất cả devices
tailscale status --peers

# Disconnect
sudo tailscale down

# Reconnect
sudo tailscale up

# Xem logs
sudo journalctl -u tailscaled
```

### ZeroTier

```bash
# Xem networks đang join
sudo zerotier-cli listnetworks

# Xem IP
sudo zerotier-cli listnetworks | grep 'portDeviceName'

# Leave network
sudo zerotier-cli leave <network-id>

# Rejoin
sudo zerotier-cli join <network-id>

# Show info
sudo zerotier-cli info
```

---

## 🐛 Troubleshooting

### Không ping được

**Tailscale:**
```bash
# Check service
sudo systemctl status tailscaled

# Restart
sudo systemctl restart tailscaled
sudo tailscale up
```

**ZeroTier:**
```bash
# Check service
sudo systemctl status zerotier-one

# Restart
sudo systemctl restart zerotier-one
```

### Firewall blocking

**Linux:**
```bash
# Allow Tailscale
sudo ufw allow in on tailscale0

# Allow ZeroTier
sudo ufw allow in on zt+
```

**Windows:**
```
Windows Defender Firewall → Allow an app
→ Tìm Tailscale/ZeroTier → Allow
```

---

## 💡 Tips & Best Practices

### 1. Đặt tên devices
- Tailscale: Tự động lấy hostname
- ZeroTier: Đặt tên trên web dashboard

### 2. Static IP (ZeroTier)
- Vào web dashboard
- Click vào device
- Enable "Allow Manual IP Assignment"
- Đặt IP tĩnh (VD: 10.147.20.100)

### 3. Auto-start
```bash
# Tailscale - Tự động
sudo systemctl enable tailscaled

# ZeroTier - Tự động
sudo systemctl enable zerotier-one
```

### 4. Backup Network ID
Lưu Network ID vào file để không quên:
```bash
echo "a0cbf4b62a1234567" > ~/.zerotier_network_id
```

---

## 🌍 Kết nối từ xa

**Sau khi setup VPN:**

1. ✅ Laptop ở nhà (WiFi A)
2. ✅ Raspberry Pi ở trường (WiFi B)
3. ✅ Vẫn kết nối được vì cùng VPN
4. ✅ Mobile app ở bất cứ đâu cũng connect được backend

**Không cần:**
- ❌ Port forwarding
- ❌ Dynamic DNS
- ❌ Public IP
- ❌ Config router

---

## 📊 So sánh Network Types

| Network | IP Range | Tốc độ | Bảo mật | Kết nối từ xa |
|---------|----------|--------|---------|---------------|
| LAN | 192.168.x.x | Rất nhanh | 🔓 | ❌ Không |
| Tailscale | 100.64.x.x | Nhanh | 🔒 Cao | ✅ Có |
| ZeroTier | 10.147.x.x | Nhanh | 🔒 Cao | ✅ Có |

---

## 🎯 Kết luận

**Khuyến nghị: Dùng Tailscale**

**Lý do:**
- ✅ Setup đơn giản nhất
- ✅ Nhanh nhất (WireGuard protocol)
- ✅ UI/UX tốt nhất
- ✅ Mobile app hỗ trợ tốt
- ✅ Documentation rõ ràng

**Thời gian setup:** 10-15 phút

**Sau khi setup:**
- IP không bao giờ thay đổi
- Kết nối ổn định
- Bảo mật cao
- Truy cập từ xa dễ dàng

**🚀 Bắt đầu ngay:** https://tailscale.com/download
