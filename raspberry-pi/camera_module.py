"""
Camera Module for capturing images from Raspberry Pi Camera
Uses picamera2 library for 5MP 1080p Camera Module
"""
import time
import logging
from io import BytesIO
from PIL import Image
from picamera2 import Picamera2
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class CameraModule:
    def __init__(self):
        """Initialize the camera module"""
        self.camera = None
        self.is_initialized = False
        
    def initialize(self):
        """Initialize and configure the camera"""
        try:
            logger.info("Initializing camera...")
            self.camera = Picamera2()
            
            # Configure camera for high-quality image capture
            camera_config = self.camera.create_still_configuration(
                main={"size": config.CAMERA_RESOLUTION, "format": config.CAMERA_FORMAT}
            )
            self.camera.configure(camera_config)
            
            # Start camera
            self.camera.start()
            
            # Warm up camera
            logger.info(f"Camera warming up for {config.CAMERA_WARMUP_TIME} seconds...")
            time.sleep(config.CAMERA_WARMUP_TIME)
            
            self.is_initialized = True
            logger.info("Camera initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            return False
    
    def capture_image(self):
        """
        Capture an image and return it as bytes
        
        Returns:
            bytes: Image data in JPEG format
        """
        if not self.is_initialized:
            logger.error("Camera not initialized")
            return None
        
        try:
            # Capture image as numpy array
            logger.debug("Capturing image...")
            image_array = self.camera.capture_array()
            
            # Convert to PIL Image
            image = Image.fromarray(image_array)
            
            # Convert to JPEG bytes
            buffer = BytesIO()
            image.save(buffer, format='JPEG', quality=95)
            image_bytes = buffer.getvalue()
            
            logger.info(f"Image captured successfully ({len(image_bytes)} bytes)")
            return image_bytes
            
        except Exception as e:
            logger.error(f"Failed to capture image: {e}")
            return None
    
    def capture_image_file(self, filename):
        """
        Capture image and save to file
        
        Args:
            filename (str): Path to save the image
        """
        if not self.is_initialized:
            logger.error("Camera not initialized")
            return False
        
        try:
            self.camera.capture_file(filename)
            logger.info(f"Image saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            return False
    
    def cleanup(self):
        """Clean up camera resources"""
        if self.camera:
            logger.info("Stopping camera...")
            self.camera.stop()
            self.camera.close()
            self.is_initialized = False
            logger.info("Camera stopped")


# Test function
if __name__ == "__main__":
    print("Testing Camera Module...")
    cam = CameraModule()
    
    if cam.initialize():
        print("Camera initialized successfully")
        
        # Capture test image
        image_data = cam.capture_image()
        if image_data:
            print(f"Captured image: {len(image_data)} bytes")
            
            # Save test image
            with open("test_capture.jpg", "wb") as f:
                f.write(image_data)
            print("Test image saved as test_capture.jpg")
        
        cam.cleanup()
    else:
        print("Failed to initialize camera")
