"""
Motor Controller for Servo and Conveyor Motors
- Servo Motor: MG996R for sorting direction
- Conveyor Motor: JGB37-545 controlled via L298N driver
"""
import time
import logging

try:
    import RPi.GPIO as GPIO
except ImportError:
    print("⚠️  RPi.GPIO không được cài đặt. Chạy: pip install RPi.GPIO")
    print("   Hoặc chạy: ./start.sh để cài đặt đầy đủ")
    raise

try:
    import config
except ImportError:
    print("⚠️  Không thể import config.py")
    print("   Đảm bảo bạn đang chạy từ thư mục dự án")
    raise

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class MotorController:
    def __init__(self):
        """Initialize motor controller"""
        self.servo_pwm = None
        self.conveyor_pwm = None
        self.is_initialized = False
        self.current_servo_angle = config.SERVO_ANGLE_CENTER
        self.current_conveyor_speed = 0
        self.motor_start_time = None
        
    def initialize(self):
        """Initialize GPIO pins and PWM for motors"""
        try:
            logger.info("Initializing motor controller...")
            
            # Set GPIO mode to BCM
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Setup Servo Motor (PWM)
            GPIO.setup(config.SERVO_PIN, GPIO.OUT)
            self.servo_pwm = GPIO.PWM(config.SERVO_PIN, config.SERVO_FREQUENCY)
            self.servo_pwm.start(0)
            
            # Setup Conveyor Motor (L298N)
            GPIO.setup(config.CONVEYOR_ENABLE_PIN, GPIO.OUT)
            GPIO.setup(config.CONVEYOR_IN1_PIN, GPIO.OUT)
            GPIO.setup(config.CONVEYOR_IN2_PIN, GPIO.OUT)
            
            # Setup PWM for speed control
            self.conveyor_pwm = GPIO.PWM(config.CONVEYOR_ENABLE_PIN, 1000)  # 1kHz
            self.conveyor_pwm.start(0)
            
            # Initialize to neutral positions
            self.set_servo_center()
            self.stop_conveyor()
            
            self.is_initialized = True
            logger.info("Motor controller initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize motor controller: {e}")
            return False
    
    def _angle_to_duty_cycle(self, angle):
        """
        Convert angle (0-180) to duty cycle percentage
        Optimized for 6V power supply via LM2596
        
        Args:
            angle (float): Servo angle in degrees (0-180)
            
        Returns:
            float: Duty cycle percentage
        """
        # Map angle to duty cycle range (calibrated for 6V operation)
        duty = config.SERVO_MIN_DUTY + (angle / 180.0) * (config.SERVO_MAX_DUTY - config.SERVO_MIN_DUTY)
        return duty
    
    def set_servo_angle(self, angle):
        """
        Set servo to specific angle
        
        Args:
            angle (float): Target angle in degrees (0-180)
        """
        if not self.is_initialized:
            logger.error("Motor controller not initialized")
            return False
        
        try:
            # Apply safety limits from config
            angle = max(config.SERVO_MIN_ANGLE, min(config.SERVO_MAX_ANGLE, angle))
            
            # Skip if already at target position
            if abs(angle - self.current_servo_angle) < 1.0:
                logger.debug(f"Servo already at {angle}°")
                return True
            
            duty = self._angle_to_duty_cycle(angle)
            
            # Send PWM signal
            self.servo_pwm.ChangeDutyCycle(duty)
            time.sleep(0.5)  # Increased wait time for servo to reach position
            self.servo_pwm.ChangeDutyCycle(0)  # Stop sending pulses to prevent jitter
            
            # Update current position
            self.current_servo_angle = angle
            
            logger.debug(f"Servo set to {angle}° (duty: {duty:.2f}%)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set servo angle: {e}")
            return False
    
    def set_servo_left(self):
        """Set servo to left position (for 'other' objects)"""
        logger.info("Sorting LEFT (other object)")
        return self.set_servo_angle(config.SERVO_ANGLE_LEFT)
    
    def set_servo_center(self):
        """Set servo to center position (for fresh fruit - straight)"""
        logger.info("Sorting CENTER (fresh fruit)")
        return self.set_servo_angle(config.SERVO_ANGLE_CENTER)
    
    def set_servo_right(self):
        """Set servo to right position (for spoiled fruit)"""
        logger.info("Sorting RIGHT (spoiled fruit)")
        return self.set_servo_angle(config.SERVO_ANGLE_RIGHT)
    
    def start_conveyor(self, speed=None):
        """
        Start conveyor belt at specified speed
        
        Args:
            speed (int): Speed percentage (0-100), defaults to config value
        """
        if not self.is_initialized:
            logger.error("Motor controller not initialized")
            return False
        
        try:
            if speed is None:
                speed = config.CONVEYOR_SPEED
            
            # Apply safety speed limit
            speed = max(0, min(config.CONVEYOR_MAX_SPEED, speed))
            
            # Set direction (forward)
            GPIO.output(config.CONVEYOR_IN1_PIN, GPIO.HIGH)
            GPIO.output(config.CONVEYOR_IN2_PIN, GPIO.LOW)
            
            # Soft start if starting from stopped
            if self.current_conveyor_speed == 0:
                logger.debug("Soft starting conveyor...")
                for ramp_speed in range(0, speed, 10):
                    self.conveyor_pwm.ChangeDutyCycle(ramp_speed)
                    time.sleep(0.05)
            
            # Set final speed
            self.conveyor_pwm.ChangeDutyCycle(speed)
            self.current_conveyor_speed = speed
            
            # Track motor start time for timeout
            if self.motor_start_time is None:
                self.motor_start_time = time.time()
            
            logger.debug(f"Conveyor started at {speed}% speed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start conveyor: {e}")
            return False
    
    def stop_conveyor(self):
        """Stop conveyor belt"""
        if not self.is_initialized:
            return False
        
        try:
            GPIO.output(config.CONVEYOR_IN1_PIN, GPIO.LOW)
            GPIO.output(config.CONVEYOR_IN2_PIN, GPIO.LOW)
            self.conveyor_pwm.ChangeDutyCycle(0)
            
            # Reset tracking
            self.current_conveyor_speed = 0
            self.motor_start_time = None
            
            logger.debug("Conveyor stopped")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop conveyor: {e}")
            return False
    
    def sort_fruit(self, classification):
        """
        Perform sorting action based on classification
        
        Args:
            classification (str): Classification result
        """
        logger.info(f"Sorting fruit: {classification}")
        
        # Stop conveyor for sorting
        self.stop_conveyor()
        time.sleep(config.CONVEYOR_STOP_TIME)
        
        # Set servo based on classification
        if classification == config.CLASSIFICATION_FRESH:
            self.set_servo_center()  # Straight
        elif classification == config.CLASSIFICATION_SPOILED:
            self.set_servo_right()   # Right
        elif classification == config.CLASSIFICATION_OTHER:
            self.set_servo_left()    # Left
        else:
            logger.warning(f"Unknown classification: {classification}")
            self.set_servo_center()  # Default to center
        
        # Wait for sorting, then resume conveyor
        time.sleep(config.CONVEYOR_RESUME_DELAY)
        self.start_conveyor()
    
    def cleanup(self):
        """Clean up GPIO resources"""
        if self.is_initialized:
            logger.info("Cleaning up motor controller...")
            
            # Stop all motors
            if self.servo_pwm:
                self.servo_pwm.stop()
            if self.conveyor_pwm:
                self.conveyor_pwm.stop()
            
            # Clean up GPIO
            GPIO.cleanup()
            
            self.is_initialized = False
            logger.info("Motor controller cleaned up")


# Test function
if __name__ == "__main__":
    print("Testing Motor Controller...")
    controller = MotorController()
    
    if controller.initialize():
        print("Motor controller initialized")
        
        # Test servo positions
        print("\nTesting servo positions...")
        print("Left position...")
        controller.set_servo_left()
        time.sleep(2)
        
        print("Center position...")
        controller.set_servo_center()
        time.sleep(2)
        
        print("Right position...")
        controller.set_servo_right()
        time.sleep(2)
        
        print("Back to center...")
        controller.set_servo_center()
        time.sleep(2)
        
        # Test conveyor
        print("\nTesting conveyor...")
        print("Starting conveyor...")
        controller.start_conveyor()
        time.sleep(3)
        
        print("Stopping conveyor...")
        controller.stop_conveyor()
        time.sleep(1)
        
        # Test sorting
        print("\nTesting sorting action...")
        controller.start_conveyor()
        time.sleep(2)
        controller.sort_fruit(config.CLASSIFICATION_SPOILED)
        time.sleep(3)
        
        controller.stop_conveyor()
        controller.cleanup()
        print("\nTest complete!")
    else:
        print("Failed to initialize motor controller")
