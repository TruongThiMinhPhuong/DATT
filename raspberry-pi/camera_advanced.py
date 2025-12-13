#!/usr/bin/env python3
"""
Advanced Camera Processing Extensions
Additional methods for enhanced camera functionality
"""

import time
import logging
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO

# Setup logging
logger = logging.getLogger(__name__)

class CameraAdvancedMethods:
    """
    Additional advanced methods for camera processing
    This is a mixin class to extend CameraModule
    """
    
    def _enhance_image(self, image):
        """Apply advanced image enhancement for AI processing"""
        try:
            # 1. Brightness adjustment
            if self.brightness_adjust != 0:
                enhancer = ImageEnhance.Brightness(image)
                factor = 1.0 + (self.brightness_adjust / 100.0)
                image = enhancer.enhance(factor)
            
            # 2. Contrast enhancement
            if self.contrast_adjust != 1.0:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(self.contrast_adjust)
            
            # 3. Color saturation enhancement
            if self.saturation_adjust != 1.0:
                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(self.saturation_adjust)
            
            # 4. Sharpness enhancement for AI detection
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)  # Slight sharpening
            
            # 5. Noise reduction (gentle blur for noise)
            if self.noise_reduction:
                # Only apply if image is noisy (detected by high variance)
                img_array = np.array(image)
                if np.var(img_array) > 1000:  # High variance indicates noise
                    image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # 6. Color balance optimization for fruit detection
            image = self._optimize_for_fruit_detection(image)
            
            logger.debug("Image enhancement completed")
            return image
            
        except Exception as e:
            logger.error(f"Image enhancement failed: {e}")
            return image  # Return original if enhancement fails
    
    def _optimize_for_fruit_detection(self, image):
        """Optimize image specifically for fruit detection AI"""
        try:
            # Convert to numpy for processing
            img_array = np.array(image)
            
            # Enhance red and orange channels (typical fruit colors)
            img_array[:, :, 0] = np.clip(img_array[:, :, 0] * 1.1, 0, 255)  # Red
            img_array[:, :, 1] = np.clip(img_array[:, :, 1] * 1.05, 0, 255) # Green (for contrast)
            
            # Reduce blue noise (common in artificial lighting)
            img_array[:, :, 2] = np.clip(img_array[:, :, 2] * 0.95, 0, 255)  # Blue
            
            # Convert back to PIL
            return Image.fromarray(img_array.astype(np.uint8))
            
        except Exception as e:
            logger.debug(f"Fruit optimization skipped: {e}")
            return image

    def set_camera_settings(self, brightness=None, contrast=None, saturation=None, quality=None):
        """
        Update camera settings dynamically
        
        Args:
            brightness (int): -100 to 100
            contrast (float): 0.5 to 2.0
            saturation (float): 0.0 to 2.0
            quality (int): JPEG quality 1-100
        """
        if brightness is not None:
            self.brightness_adjust = max(-100, min(100, brightness))
        if contrast is not None:
            self.contrast_adjust = max(0.5, min(2.0, contrast))
        if saturation is not None:
            self.saturation_adjust = max(0.0, min(2.0, saturation))
        if quality is not None:
            self.jpeg_quality = max(1, min(100, quality))
        
        logger.info(f"Camera settings updated: brightness={self.brightness_adjust}, "
                   f"contrast={self.contrast_adjust:.1f}, saturation={self.saturation_adjust:.1f}, "
                   f"quality={self.jpeg_quality}")

    def get_camera_stats(self):
        """Get camera performance statistics"""
        return {
            "camera_type": self.camera_type,
            "capture_count": self.capture_count,
            "last_capture_time": self.last_capture_time,
            "is_initialized": self.is_initialized,
            "settings": {
                "brightness": self.brightness_adjust,
                "contrast": self.contrast_adjust,
                "saturation": self.saturation_adjust,
                "quality": self.jpeg_quality
            }
        }

    def capture_burst(self, count=3, delay=0.5):
        """
        Capture multiple images in quick succession
        
        Args:
            count (int): Number of images to capture
            delay (float): Delay between captures in seconds
            
        Returns:
            list: List of image bytes
        """
        if not self.is_initialized:
            logger.error("Camera not initialized")
            return []
        
        images = []
        logger.info(f"Starting burst capture: {count} images")
        
        for i in range(count):
            image_bytes = self.capture_image(enhance=True)
            if image_bytes:
                images.append(image_bytes)
                logger.debug(f"Burst image {i+1}/{count} captured")
            
            if i < count - 1:  # Don't delay after last image
                time.sleep(delay)
        
        logger.info(f"Burst capture completed: {len(images)} images")
        return images

    def preview_mode(self, duration=10):
        """
        Enter preview mode for camera setup and testing
        
        Args:
            duration (int): Preview duration in seconds
        """
        if not self.is_initialized:
            logger.error("Camera not initialized for preview")
            return False
        
        logger.info(f"Starting preview mode for {duration} seconds...")
        
        try:
            if self.camera_type == 'picamera2':
                # Enable preview for picamera2
                self.camera.start_preview()
                time.sleep(duration)
                self.camera.stop_preview()
            else:
                # For OpenCV, capture and display frames
                import cv2
                start_time = time.time()
                while time.time() - start_time < duration:
                    ret, frame = self.cap.read()
                    if ret:
                        cv2.imshow('Camera Preview', frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                cv2.destroyAllWindows()
            
            logger.info("Preview mode completed")
            return True
            
        except Exception as e:
            logger.error(f"Preview mode failed: {e}")
            return False

    def get_enhancement_settings(self):
        """
        Get available enhancement settings
        
        Returns:
            dict: Available enhancement options
        """
        return {
            'brightness_range': (-1.0, 1.0),
            'contrast_range': (0.1, 3.0),
            'saturation_range': (0.1, 3.0),
            'sharpness_range': (0.1, 3.0),
            'available_modes': ['bright', 'dark', 'low_light', 'high_contrast'],
            'default_settings': {
                'brightness': 0.1,
                'contrast': 1.2,
                'saturation': 1.1,
                'sharpness': 1.3
            }
        }

# Test function for advanced methods
if __name__ == "__main__":
    print("Advanced Camera Methods Module")
    print("This module provides extensions for CameraModule")
    print("Import this in main camera_module.py to use advanced features")