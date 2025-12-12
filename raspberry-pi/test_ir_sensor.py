#!/usr/bin/env python3
"""
IR Sensor Test Script
Test the IR sensor before running the full system
"""
import RPi.GPIO as GPIO
import time
import sys

# IR Sensor Configuration
IR_PIN = 24  # GPIO 24 (Physical Pin 18)

def test_ir_sensor():
    """Test IR sensor functionality"""
    print("="*50)
    print("IR SENSOR TEST SCRIPT")
    print("="*50)
    print(f"GPIO Pin: {IR_PIN} (BCM Mode)")
    print("="*50)
    
    try:
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(IR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        print("\n✓ GPIO configured successfully")
        print("\nInstructions:")
        print("1. Place an object in front of the IR sensor")
        print("2. Remove the object")
        print("3. Adjust the potentiometer if needed")
        print("4. Press Ctrl+C to exit\n")
        print("-"*50)
        
        detection_count = 0
        last_state = GPIO.LOW
        
        while True:
            current_state = GPIO.input(IR_PIN)
            
            # Detect state change
            if current_state == GPIO.HIGH and last_state == GPIO.LOW:
                detection_count += 1
                print(f"\n[{time.strftime('%H:%M:%S')}] ✓ OBJECT DETECTED! (Count: {detection_count})")
                print("    → This would trigger a photo capture")
            elif current_state == GPIO.LOW and last_state == GPIO.HIGH:
                print(f"[{time.strftime('%H:%M:%S')}] ○ Object removed")
            
            # Display current state
            if current_state == GPIO.HIGH:
                print("█", end='', flush=True)  # Object present
            else:
                print("░", end='', flush=True)  # No object
            
            last_state = current_state
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*50)
        print(f"Test completed!")
        print(f"Total detections: {detection_count}")
        print("="*50)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up")


def check_gpio_status():
    """Check if GPIO is accessible"""
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(IR_PIN, GPIO.IN)
        status = GPIO.input(IR_PIN)
        GPIO.cleanup()
        return True, status
    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    print("\nChecking GPIO access...")
    
    success, result = check_gpio_status()
    
    if not success:
        print(f"✗ Cannot access GPIO: {result}")
        print("\nTry running with sudo:")
        print("  sudo python3 test_ir_sensor.py")
        sys.exit(1)
    
    print(f"✓ GPIO accessible (current value: {result})")
    print()
    
    test_ir_sensor()
