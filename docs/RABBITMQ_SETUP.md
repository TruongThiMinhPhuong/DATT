# 🐰 RabbitMQ Setup Guide - Windows

Hướng dẫn cài đặt RabbitMQ trên Windows.

---

## 🚀 Cài đặt bằng Chocolatey (Dễ nhất)

### Bước 1: Cài Chocolatey

**Mở PowerShell as Administrator:**

```powershell
# Check xem đã có chưa
choco --version

# Nếu chưa có, cài mới:
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### Bước 2: Cài RabbitMQ

```powershell
# Cài RabbitMQ (tự động cài cả Erlang)
choco install rabbitmq -y
```

**Đợi 2-3 phút...**

### Bước 3: Enable Management UI

```powershell
# Navigate to RabbitMQ folder
cd "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.13.0\sbin"

# Enable plugin
.\rabbitmq-plugins.bat enable rabbitmq_management

# Restart service
net stop RabbitMQ
net start RabbitMQ
```

### Bước 4: Test

**Mở browser:** http://localhost:15672

**Login:**
- Username: `guest`
- Password: `guest`

✅ **Thấy Management UI = Thành công!**

---

## 🔧 Cài đặt Manual (Không dùng Chocolatey)

### Bước 1: Cài Erlang

1. Download: https://www.erlang.org/downloads
2. Chọn: **OTP 26.x Windows 64-bit**
3. Run installer → Install

### Bước 2: Cài RabbitMQ

1. Download: https://www.rabbitmq.com/docs/install-windows
2. Chọn: **RabbitMQ Server** (Latest)
3. Run installer → Install

### Bước 3: Setup

**Command Prompt as Admin:**

```cmd
cd "C:\Program Files\RabbitMQ Server\rabbitmq_server-4.2.1\sbin"
rabbitmq-plugins.bat enable rabbitmq_management
net start RabbitMQ
```

---

## ✅ Kiểm tra RabbitMQ

### 1. Check Service

```powershell
Get-Service -Name RabbitMQ
# Status: Running ✅
```

### 2. Check Ports

```powershell
netstat -ano | findstr "5672"
netstat -ano | findstr "15672"
```

**Ports:**
- `5672` - Client connections
- `15672` - Management UI

### 3. Check Web UI

http://localhost:15672

---

## 🔑 Tạo User mới (Tùy chọn)

```powershell
cd "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.13.0\sbin"

# Tạo user
.\rabbitmqctl.bat add_user admin password123

# Set permissions
.\rabbitmqctl.bat set_user_tags admin administrator
.\rabbitmqctl.bat set_permissions -p / admin "phuong123" "phuong123" "phuong123"

# List users
.\rabbitmqctl.bat list_users
```

---

## 🚀 Chạy với Backend

**Backend `.env`:**
```env
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=phuong123
```

**Start backend:**
```bash
cd backend
python classifier_service.py  # Terminal 1
python api.py                 # Terminal 2
```

**Check logs:**
```
INFO - Connected to RabbitMQ ✅
```

---

## 🐛 Troubleshooting

### Service không start

```powershell
# Check logs
cd "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.13.0\sbin"
.\rabbitmq-diagnostics.bat status

# Reinstall
choco uninstall rabbitmq -y
choco install rabbitmq -y
```

### Port conflicts

```powershell
# Check what's using port 5672
netstat -ano | findstr "5672"

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Management UI không load

```powershell
# Re-enable plugin
cd "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.13.0\sbin"
.\rabbitmq-plugins.bat disable rabbitmq_management
.\rabbitmq-plugins.bat enable rabbitmq_management
net stop RabbitMQ
net start RabbitMQ
```

---

## 🎯 Commands hữu ích

```powershell
# Start service
net start RabbitMQ

# Stop service
net stop RabbitMQ

# Restart service
net stop RabbitMQ && net start RabbitMQ

# Check status
Get-Service -Name RabbitMQ

# View logs
cd "C:\Users\<username>\AppData\Roaming\RabbitMQ\log"
type rabbit@<hostname>.log

# List queues
cd "C:\Program Files\RabbitMQ Server\rabbitmq_server-3.13.0\sbin"
.\rabbitmqctl.bat list_queues
```

---

## 🔄 Auto-start on Windows boot

RabbitMQ tự động chạy khi Windows khởi động (Windows Service).

**Disable auto-start (nếu cần):**
```powershell
Set-Service -Name RabbitMQ -StartupType Manual
```

**Enable auto-start:**
```powershell
Set-Service -Name RabbitMQ -StartupType Automatic
```

---

✅ **Setup hoàn tất! RabbitMQ đã sẵn sàng.**
