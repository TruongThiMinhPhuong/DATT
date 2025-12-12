"""
Configuration file for Raspberry Pi Edge Module
"""
import os
from dotenv import load_dotenv

load_dotenv()

# RabbitMQ Configuration
# Use Tailscale IP for stable connection (recommended)
# Get IP with: tailscale ip -4
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', '100.64.1.2')  # Tailscale IP of backend laptop
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')

# Queue Names
IMAGE_QUEUE = 'fruit_images'
RESULT_QUEUE = 'classification_results'

# GPIO Pin Configuration (BCM Mode)
SERVO_PIN = 18  # PWM capable pin for MG996R servo
CONVEYOR_ENABLE_PIN = 17  # L298N Enable A
CONVEYOR_IN1_PIN = 27  # L298N Input 1
CONVEYOR_IN2_PIN = 22  # L298N Input 2

# Servo Angles (MG996R: 0-180 degrees)
SERVO_ANGLE_LEFT = 30    # For "other" objects
SERVO_ANGLE_CENTER = 90  # For fresh fruit (straight)
SERVO_ANGLE_RIGHT = 150  # For spoiled fruit

# Servo PWM Configuration
SERVO_FREQUENCY = 50  # 50Hz for standard servo
SERVO_MIN_DUTY = 2.5  # Minimum duty cycle (0 degrees)
SERVO_MAX_DUTY = 12.5  # Maximum duty cycle (180 degrees)

# Conveyor Motor Configuration
CONVEYOR_SPEED = 75  # Speed percentage (0-100)
CONVEYOR_STOP_TIME = 2.0  # Seconds to stop for sorting
CONVEYOR_RESUME_DELAY = 0.5  # Delay before resuming

# Camera Configuration
CAMERA_RESOLUTION = (1920, 1080)  # 5MP camera supports 1080p
CAMERA_FORMAT = 'RGB888'
CAMERA_WARMUP_TIME = 2  # Seconds to warm up camera

# Trigger Configuration (Multi-Mode Support)
TRIGGER_MODE = 'ir_sensor'  # Options: 'ir_sensor', 'time_based', 'manual', 'continuous'
CAPTURE_INTERVAL = 5.0  # Seconds between captures in time_based mode
CAPTURE_DELAY = 0.3  # Delay before capture

# IR Sensor Configuration
IR_SENSOR_PIN = 24  # IR sensor output pin (FC-51 or similar)
IR_DEBOUNCE_TIME = 2.0  # Minimum seconds between IR detections

# Emergency Stop Configuration
EMERGENCY_STOP_PIN = 23  # Physical emergency stop button (optional)
USE_EMERGENCY_STOP = False  # Set to True if emergency stop button is installed

# Motor Safety Limits
SERVO_MIN_ANGLE = 0  # Minimum safe servo angle
SERVO_MAX_ANGLE = 180  # Maximum safe servo angle
CONVEYOR_MAX_SPEED = 95  # Maximum conveyor speed (safety limit)
MOTOR_TIMEOUT = 30  # Maximum continuous motor run time (seconds)

# System Configuration
RETRY_DELAY = 5  # Seconds to wait before reconnecting
MAX_RETRIES = 3  # Maximum retry attempts for message sending
LOG_LEVEL = 'INFO'

# Classification Categories
CLASSIFICATION_FRESH = 'fresh_fruit'
CLASSIFICATION_SPOILED = 'spoiled_fruit'
CLASSIFICATION_OTHER = 'other'
