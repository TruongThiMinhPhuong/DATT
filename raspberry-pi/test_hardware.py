#!/usr/bin/env python3
"""
Hardware Testing Script for Fruit Sorting System
Test all components including LM2596 power supply
"""
try:
    import RPi.GPIO as GPIO
except ImportError:
    print("❌ RPi.GPIO không được cài đặt. Chạy: pip install RPi.GPIO")
    print("   Hoặc chạy: ./start.sh để cài đặt đầy đủ")
    exit(1)

import time
import sys
import os

try:
    import config
except ImportError:
    print("❌ Không thể import config.py")
    print("   Đảm bảo bạn đang chạy từ thư mục dự án")
    exit(1)

def test_power_supply():
    """Test power supply voltages"""
    print("🔋 POWER SUPPLY TEST")
    print("-" * 30)
    print(f"Expected Servo Voltage: {config.LM2596_OUTPUT_VOLTAGE}V")
    print(f"Expected Motor Voltage: {config.LM2596_INPUT_VOLTAGE}V")
    print(f"LM2596 Max Current: {config.LM2596_MAX_CURRENT}A")
    print("\n⚠️  MANUALLY VERIFY with multimeter:")
    print("   1. Main PSU output: 12V ±0.5V")
    print("   2. LM2596 output: 6.0V ±0.1V")
    print("   3. Pi 5V rail: 5.0V ±0.25V")
    
    input("\nPress Enter after verifying voltages...")

def test_servo():
    """Test servo motor with 6V power supply"""
    print("\n🔄 SERVO MOTOR TEST (MG996R @ 6V)")
    print("-" * 35)
    
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(config.SERVO_PIN, GPIO.OUT)
        
        # Create PWM instance
        servo_pwm = GPIO.PWM(config.SERVO_PIN, config.SERVO_FREQUENCY)
        servo_pwm.start(0)
        
        print("Testing servo movement...")
        
        # Test sequence
        positions = [
            (config.SERVO_ANGLE_LEFT, "LEFT (Other)"),
            (config.SERVO_ANGLE_CENTER, "CENTER (Fresh)"),
            (config.SERVO_ANGLE_RIGHT, "RIGHT (Spoiled)"),
            (config.SERVO_ANGLE_CENTER, "CENTER (Home)")
        ]
        
        for angle, description in positions:
            duty = config.SERVO_MIN_DUTY + (angle / 180.0) * (config.SERVO_MAX_DUTY - config.SERVO_MIN_DUTY)
            print(f"   → {description}: {angle}° (duty: {duty:.2f}%)")
            
            servo_pwm.ChangeDutyCycle(duty)
            time.sleep(1.5)  # Wait for movement
            servo_pwm.ChangeDutyCycle(0)  # Stop signal
            time.sleep(0.5)
        
        servo_pwm.stop()
        print("✅ Servo test completed")
        
    except Exception as e:
        print(f"❌ Servo test failed: {e}")

def test_conveyor():
    """Test conveyor motor"""
    print("\n🚚 CONVEYOR MOTOR TEST (JGB37-545)")
    print("-" * 35)
    
    try:
        # Setup L298N pins
        GPIO.setup(config.CONVEYOR_ENABLE_PIN, GPIO.OUT)
        GPIO.setup(config.CONVEYOR_IN1_PIN, GPIO.OUT)
        GPIO.setup(config.CONVEYOR_IN2_PIN, GPIO.OUT)
        
        # Setup PWM
        conveyor_pwm = GPIO.PWM(config.CONVEYOR_ENABLE_PIN, 1000)
        conveyor_pwm.start(0)
        
        print("Testing conveyor movement...")
        
        # Forward direction
        GPIO.output(config.CONVEYOR_IN1_PIN, GPIO.HIGH)
        GPIO.output(config.CONVEYOR_IN2_PIN, GPIO.LOW)
        
        for speed in [30, 50, 75, 0]:
            print(f"   → Speed: {speed}%")
            conveyor_pwm.ChangeDutyCycle(speed)
            time.sleep(2)
        
        conveyor_pwm.stop()
        print("✅ Conveyor test completed")
        
    except Exception as e:
        print(f"❌ Conveyor test failed: {e}")

def test_ir_sensor():
    """Test IR sensor"""
    print("\n👁️  IR SENSOR TEST (FC-51)")
    print("-" * 25)
    
    try:
        GPIO.setup(config.IR_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        print("Monitoring IR sensor for 10 seconds...")
        print("Place object in front of sensor to test")
        
        start_time = time.time()
        detections = 0
        last_state = GPIO.LOW
        
        while time.time() - start_time < 10:
            current_state = GPIO.input(config.IR_SENSOR_PIN)
            
            if current_state == GPIO.HIGH and last_state == GPIO.LOW:
                detections += 1
                print(f"   ✓ Detection #{detections}")
            
            last_state = current_state
            time.sleep(0.1)
        
        print(f"✅ IR sensor test completed - {detections} detections")
        
    except Exception as e:
        print(f"❌ IR sensor test failed: {e}")

def test_system_integration():
    """Test full system integration"""
    print("\n🎯 SYSTEM INTEGRATION TEST")
    print("-" * 30)
    
    try:
        print("Simulating fruit detection cycle...")
        
        # Setup all components
        GPIO.setup(config.SERVO_PIN, GPIO.OUT)
        GPIO.setup(config.CONVEYOR_ENABLE_PIN, GPIO.OUT)
        GPIO.setup(config.CONVEYOR_IN1_PIN, GPIO.OUT)
        GPIO.setup(config.CONVEYOR_IN2_PIN, GPIO.OUT)
        GPIO.setup(config.IR_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        servo_pwm = GPIO.PWM(config.SERVO_PIN, config.SERVO_FREQUENCY)
        conveyor_pwm = GPIO.PWM(config.CONVEYOR_ENABLE_PIN, 1000)
        
        servo_pwm.start(0)
        conveyor_pwm.start(0)
        
        # Start conveyor
        print("   1. Starting conveyor...")
        GPIO.output(config.CONVEYOR_IN1_PIN, GPIO.HIGH)
        GPIO.output(config.CONVEYOR_IN2_PIN, GPIO.LOW)
        conveyor_pwm.ChangeDutyCycle(config.CONVEYOR_SPEED)
        time.sleep(3)
        
        # Stop for sorting
        print("   2. Stopping for sorting...")
        conveyor_pwm.ChangeDutyCycle(0)
        time.sleep(0.5)
        
        # Sort to fresh fruit position
        print("   3. Sorting to FRESH position...")
        duty = config.SERVO_MIN_DUTY + (config.SERVO_ANGLE_CENTER / 180.0) * (config.SERVO_MAX_DUTY - config.SERVO_MIN_DUTY)
        servo_pwm.ChangeDutyCycle(duty)
        time.sleep(2)
        servo_pwm.ChangeDutyCycle(0)
        
        # Resume conveyor
        print("   4. Resuming conveyor...")
        time.sleep(config.CONVEYOR_RESUME_DELAY)
        conveyor_pwm.ChangeDutyCycle(config.CONVEYOR_SPEED)
        time.sleep(2)
        
        # Stop everything
        conveyor_pwm.ChangeDutyCycle(0)
        servo_pwm.stop()
        conveyor_pwm.stop()
        
        print("✅ Integration test completed")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")

def main():
    """Main testing function"""
    print("="*50)
    print("🧪 HARDWARE TEST SUITE")
    print("🍓 AI Fruit Sorting System")
    print("="*50)
    
    try:
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Run tests
        test_power_supply()
        test_servo()
        test_conveyor()
        test_ir_sensor()
        test_system_integration()
        
        print("\n" + "="*50)
        print("🎉 ALL TESTS COMPLETED!")
        print("="*50)
        print("\n📋 Next Steps:")
        print("   1. Verify all connections are secure")
        print("   2. Check LM2596 output voltage (6.0V)")
        print("   3. Test with actual fruit samples")
        print("   4. Run full system: ./run.sh")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
    finally:
        GPIO.cleanup()
        print("🧹 GPIO cleaned up")

if __name__ == "__main__":
    main()