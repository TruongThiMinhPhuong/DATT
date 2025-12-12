# 🌐 Tailscale Setup - VPN với IP cố định

Hướng dẫn setup Tailscale để có IP cố định, kết nối ổn định từ xa.

---

## 🎯 Tại sao dùng Tailscale?

- ✅ **IP cố định** - Không bao giờ thay đổi
- ✅ **Kết nối từ xa** - Ở bất cứ đâu có Internet
- ✅ **Bảo mật** - Mã hóa WireGuard
- ✅ **Miễn phí** - 20 devices
- ✅ **Dễ setup** - 10 phút

---

## 🚀 Cài đặt

### Bước 1: Tạo tài khoản

1. Truy cập: https://tailscale.com
2. Sign up với Google/GitHub/Email
3. Tài khoản miễn phí - 20 devices

### Bước 2: Install trên Laptop (Backend)

**Windows:**
```powershell
# Download: https://tailscale.com/download/windows
# Chạy installer → Connect → Đăng nhập
```

**Hoặc dùng Chocolatey:**
```powershell
choco install tailscale -y
tailscale up
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
# Install
curl -fsSL https://tailscale.com/install.sh | sh

# Connect (sẽ hiện link để đăng nhập)
sudo tailscale up

# Copy link và mở trên browser để xác thực
```

### Bước 4: Lấy IP

**Laptop:**
```powershell
tailscale ip -4
# Ví dụ: 100.64.1.2
```

**Raspberry Pi:**
```bash
sudo tailscale ip -4
# Ví dụ: 100.64.1.3
```

---

## ⚙️ Cấu hình Project

### 1. Raspberry Pi Config

**File: `raspberry-pi/config.py`**

```python
# Dòng 18: Dùng IP Tailscale của laptop
RABBITMQ_HOST = '100.64.1.2'  # Thay bằng IP Tailscale laptop của bạn
```

### 2. Backend Hardware API

**File: `backend/hardware_api.py`**

```python
# Dòng 29: Dùng IP Tailscale của Pi
RASPBERRY_PI_HOST = "http://100.64.1.3:5000"  # Thay bằng IP Tailscale Pi của bạn
```

### 3. Mobile App (Tùy chọn)

**File: `mobile_app/lib/services/api_service.dart`**

```dart
// Dòng 6: Dùng IP Tailscale của laptop
ApiService({this.baseUrl = 'http://100.64.1.2:8000'});
```

---

## ✅ Test kết nối

**Từ Raspberry Pi, ping laptop:**
```bash
ping 100.64.1.2
# Nếu ping được → Thành công!
```

**Từ laptop, ping Pi:**
```powershell
ping 100.64.1.3
```

---

## 🚀 Chạy hệ thống

**Laptop:**
```bash
cd D:\DATT
start-backend.bat
```

**Raspberry Pi:**
```bash
cd raspberry-pi
./start.sh
```

**Giờ hoạt động từ xa!** Laptop và Pi có thể ở khác mạng WiFi.

---

## 🔧 Commands hữu ích

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
```

---

## 🐛 Troubleshooting

### Không ping được

```bash
# Check service
sudo systemctl status tailscaled  # Linux
Get-Service Tailscale  # Windows

# Restart
sudo systemctl restart tailscaled  # Linux
Restart-Service Tailscale  # Windows
```

### IP thay đổi

Tailscale IP **không bao giờ đổi** trừ khi:
- Xóa device khỏi Tailscale admin
- Reinstall Tailscale

→ Yên tâm sử dụng!

---

## 💡 Tips

### 1. Đặt tên devices

Tailscale tự động lấy hostname. Để đổi tên:
- Vào https://login.tailscale.com/admin/machines
- Click device → Rename

### 2. Auto-start

**Windows:** Tự động (registry)

**Linux:**
```bash
sudo systemctl enable tailscaled
```

**Raspberry Pi:**
```bash
sudo systemctl enable tailscaled
```

---

## 📊 So sánh với IP thường

| Network | IP | Ổn định | Từ xa | Bảo mật |
|---------|-----|---------|-------|---------|
| LAN | 192.168.x.x | ❌ Thay đổi | ❌ Không | ⚠️ Thấp |
| Tailscale | 100.64.x.x | ✅ Cố định | ✅ Có | ✅ Cao |

---

## 🎯 Kết luận

**Setup:**
1. Install Tailscale (10 phút)
2. Lấy IP (1 phút)
3. Update config (2 phút)
4. Done! ✅

**Kết quả:**
- IP không đổi
- Kết nối từ xa
- Bảo mật cao
- Không cần port forwarding

**🚀 Bắt đầu:** https://tailscale.com/download
