"""
Main Application for Raspberry Pi Fruit Sorting System
Orchestrates camera, motors, and RabbitMQ communication
"""
import time
import logging
import signal
import sys
import RPi.GPIO as GPIO
from camera_module import CameraModule
from motor_controller import MotorController
from rabbitmq_client import RabbitMQClient
import config

logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FruitSortingSystem:
    def __init__(self):
        """Initialize the fruit sorting system"""
        self.camera = CameraModule()
        self.motor = MotorController()
        self.rabbitmq = RabbitMQClient(result_callback=self.handle_classification_result)
        self.is_running = False
        self.last_ir_detection = 0  # Track last IR sensor trigger time
        
    def initialize(self):
        """Initialize all components"""
        logger.info("=== Initializing Fruit Sorting System ===")
        
        # Initialize camera
        if not self.camera.initialize():
            logger.error("Failed to initialize camera")
            return False
        
        # Initialize motor controller
        if not self.motor.initialize():
            logger.error("Failed to initialize motor controller")
            return False
        
        # Initialize RabbitMQ connection
        if not self.rabbitmq.connect():
            logger.error("Failed to connect to RabbitMQ")
            logger.info("Attempting to reconnect...")
            if not self.rabbitmq.reconnect(max_attempts=3):
                logger.error("Could not establish RabbitMQ connection")
                return False
        
        # Start consuming classification results
        self.rabbitmq.start_consuming_results()
        
        # Setup IR sensor if in IR mode
        if config.TRIGGER_MODE == 'ir_sensor':
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(config.IR_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            logger.info(f"IR sensor configured on GPIO {config.IR_SENSOR_PIN}")
        
        # Setup emergency stop if enabled
        if config.USE_EMERGENCY_STOP:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(config.EMERGENCY_STOP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            logger.info("Emergency stop button configured")
        
        logger.info("=== System Initialized Successfully ===")
        return True
    
    def handle_classification_result(self, result):
        """
        Handle classification result from backend
        
        Args:
            result (dict): Classification result from backend
                          Format: {'id': '...', 'fruit_type': 'Apple', 'confidence': 0.89, 
                                   'quality': 'Good', 'weight': 156.3}
        """
        try:
            # Backend sends: fruit_type, quality, confidence, weight
            fruit_type = result.get('fruit_type', 'Unknown')
            confidence = result.get('confidence', 0.0)
            quality = result.get('quality', 'Unknown')
            weight = result.get('weight', 0.0)
            
            logger.info(f"Classification: {fruit_type} (confidence: {confidence:.2%}, quality: {quality}, weight: {weight}g)")
            
            # Map backend response to motor classification categories
            if quality in ['Excellent', 'Good']:
                classification = config.CLASSIFICATION_FRESH
            elif quality in ['Fair', 'Poor', 'Bad']:
                classification = config.CLASSIFICATION_SPOILED
            else:
                classification = config.CLASSIFICATION_OTHER
            
            logger.info(f"Sorting as: {classification}")
            
            # Perform sorting action
            self.motor.sort_fruit(classification)
            
        except Exception as e:
            logger.error(f"Error handling classification result: {e}")
    
    def check_emergency_stop(self):
        """
        Check if emergency stop button is pressed
        
        Returns:
            bool: True if emergency stop is activated
        """
        if config.USE_EMERGENCY_STOP:
            # Button pressed = LOW (pull-up resistor)
            return GPIO.input(config.EMERGENCY_STOP_PIN) == GPIO.LOW
        return False
    
    def detect_fruit_ir(self):
        """
        Check if fruit is detected by IR sensor with debouncing
        
        Returns:
            bool: True if fruit detected and debounce time passed
        """
        # Read sensor (HIGH when object detected)
        if GPIO.input(config.IR_SENSOR_PIN) == GPIO.HIGH:
            current_time = time.time()
            # Check debounce time
            if current_time - self.last_ir_detection >= config.IR_DEBOUNCE_TIME:
                self.last_ir_detection = current_time
                return True
        return False
    
    def process_fruit(self):
        """Process detected fruit: capture image and send for classification"""
        try:
            logger.info("Fruit detected! Processing...")
            
            # Small delay for positioning
            time.sleep(config.CAPTURE_DELAY)
            
            # Capture image
            image_bytes = self.camera.capture_image()
            if not image_bytes:
                logger.error("Failed to capture image")
                return
            
            # Send image to backend for classification
            metadata = {
                'timestamp': time.time(),
                'device_id': 'rpi_conveyor_01'
            }
            
            if self.rabbitmq.send_image(image_bytes, metadata):
                logger.info("Image sent for classification")
            else:
                logger.error("Failed to send image to backend")
                # Try to reconnect
                if not self.rabbitmq.is_connected:
                    logger.info("Attempting to reconnect to RabbitMQ...")
                    self.rabbitmq.reconnect(max_attempts=3)
            
        except Exception as e:
            logger.error(f"Error processing fruit: {e}")
    
    def run(self):
        """Main operation loop"""
        logger.info("=== Starting Fruit Sorting System ===")
        logger.info(f"Trigger mode: {config.TRIGGER_MODE}")
        self.is_running = True
        
        # Start conveyor belt
        self.motor.start_conveyor()
        logger.info("Conveyor belt started")
        
        # Time-based triggering variables
        last_capture_time = 0
        
        try:
            while self.is_running:
                # Check emergency stop
                if self.check_emergency_stop():
                    logger.warning("EMERGENCY STOP ACTIVATED!")
                    self.motor.stop_conveyor()
                    while self.check_emergency_stop():
                        time.sleep(0.5)
                    logger.info("Emergency stop released, resuming...")
                    self.motor.start_conveyor()
                
                # IR Sensor mode - detect fruit presence
                if config.TRIGGER_MODE == 'ir_sensor':
                    if self.detect_fruit_ir():
                        logger.info("Fruit detected by IR sensor!")
                        self.process_fruit()
                
                # Time-based triggering
                elif config.TRIGGER_MODE == 'time_based':
                    current_time = time.time()
                    if current_time - last_capture_time >= config.CAPTURE_INTERVAL:
                        last_capture_time = current_time
                        self.process_fruit()
                
                # Continuous mode - process as fast as possible
                elif config.TRIGGER_MODE == 'continuous':
                    self.process_fruit()
                    time.sleep(config.CAPTURE_INTERVAL)
                
                # Manual mode - wait for external trigger (future: API endpoint)
                # In manual mode, just keep conveyor running
                
                # Small delay to prevent CPU overload
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            logger.info("System interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up all resources"""
        logger.info("=== Cleaning up system ===")
        self.is_running = False
        
        # Stop motors
        self.motor.stop_conveyor()
        self.motor.cleanup()  # This handles GPIO.cleanup()
        
        # Stop camera
        self.camera.cleanup()
        
        # Disconnect RabbitMQ
        self.rabbitmq.disconnect()
        
        logger.info("=== System shutdown complete ===")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("Received shutdown signal")
    sys.exit(0)


def main():
    """Main entry point"""
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and initialize system
    system = FruitSortingSystem()
    
    if system.initialize():
        # Run main loop
        system.run()
    else:
        logger.error("Failed to initialize system")
        sys.exit(1)


if __name__ == "__main__":
    main()
