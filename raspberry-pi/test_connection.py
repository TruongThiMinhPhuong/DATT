#!/usr/bin/env python3
"""
Test connection from Raspberry Pi to Laptop
Run: source venv/bin/activate && python3 test_connection.py
"""
import sys
import socket
import subprocess

def print_header(text):
    print(f"\n{'='*50}")
    print(f"  {text}")
    print('='*50)

def test_ping(host):
    """Test if host is reachable"""
    try:
        result = subprocess.run(
            ['ping', '-c', '2', '-W', '2', host],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False

def test_port(host, port, timeout=5):
    """Test if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def test_rabbitmq(host, port, user, password):
    """Test RabbitMQ connection"""
    try:
        import pika
        credentials = pika.PlainCredentials(user, password)
        params = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials,
            connection_attempts=2,
            socket_timeout=5
        )
        conn = pika.BlockingConnection(params)
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def main():
    # Load config
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        
        host = os.getenv('RABBITMQ_HOST', '100.112.253.55')
        port = int(os.getenv('RABBITMQ_PORT', 5672))
        user = os.getenv('RABBITMQ_USER', 'guest')
        password = os.getenv('RABBITMQ_PASSWORD', 'guest')
    except:
        host = '100.112.253.55'
        port = 5672
        user = 'guest'
        password = 'guest'
    
    print_header("Raspberry Pi → Laptop Connection Test")
    
    print(f"\nTarget: {host}:{port}")
    print(f"User: {user}")
    
    # Test 1: Ping
    print_header("Test 1: Network Ping")
    if test_ping(host):
        print(f"✅ Ping to {host} - OK")
    else:
        print(f"❌ Ping to {host} - FAILED")
        print("   → Kiểm tra Tailscale đang chạy trên cả 2 máy")
        print("   → Chạy 'tailscale status' để kiểm tra")
        sys.exit(1)
    
    # Test 2: Port
    print_header("Test 2: RabbitMQ Port")
    if test_port(host, port):
        print(f"✅ Port {port} is OPEN")
    else:
        print(f"❌ Port {port} is CLOSED")
        print("   → Trên LAPTOP, chạy: docker ps | grep rabbitmq")
        print("   → Hoặc: docker start rabbitmq")
        print("   → Kiểm tra Windows Firewall cho phép port 5672")
        sys.exit(1)
    
    # Test 3: RabbitMQ Connection
    print_header("Test 3: RabbitMQ Connection")
    success, error = test_rabbitmq(host, port, user, password)
    if success:
        print("✅ RabbitMQ connection - OK")
    else:
        print(f"❌ RabbitMQ connection - FAILED")
        print(f"   Error: {error}")
        print("   → Kiểm tra user/password RabbitMQ")
        print("   → Trên laptop: http://localhost:15672 để xem management")
        sys.exit(1)
    
    # Test 4: Check camera (if available)
    print_header("Test 4: Camera Module")
    try:
        from picamera2 import Picamera2
        cam = Picamera2()
        cam.close()
        print("✅ Camera module - OK")
    except Exception as e:
        print(f"⚠️  Camera module - {e}")
        print("   → Bật camera: sudo raspi-config -> Interface Options -> Camera")
    
    # Test 5: GPIO
    print_header("Test 5: GPIO Access")
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
        print("✅ GPIO access - OK")
    except Exception as e:
        print(f"⚠️  GPIO access - {e}")
    
    print_header("All Tests Completed")
    print("\n✅ Raspberry Pi sẵn sàng kết nối với Laptop!")
    print("\nĐể chạy hệ thống:")
    print("  ./start.sh")
    print("\nHoặc:")
    print("  source venv/bin/activate")
    print("  python3 main.py")

if __name__ == '__main__':
    main()
