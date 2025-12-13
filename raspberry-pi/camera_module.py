"""
Camera Module for capturing images from Raspberry Pi Camera
Supports both picamera2 (preferred) and OpenCV (fallback)
Advanced image processing and quality optimization
"""
import time
import logging
import os
from io import BytesIO
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import config

# Try picamera2 first, fallback to OpenCV
CAMERA_TYPE = None
HAS_LIBCAMERA_CONTROLS = False

try:
    from picamera2 import Picamera2
    # Remove libcamera controls import as it may not be available in all versions
    try:
        from libcamera import controls
        HAS_LIBCAMERA_CONTROLS = True
        logger = logging.getLogger(__name__)
        logger.debug("✅ libcamera controls available")
    except ImportError:
        logger = logging.getLogger(__name__)
        logger.debug("⚠️  libcamera controls not available - using basic mode")
    
    CAMERA_TYPE = 'picamera2'
    logger = logging.getLogger(__name__)
    logger.info("✅ picamera2 available - using Raspberry Pi Camera")
except ImportError:
    try:
        import cv2
        CAMERA_TYPE = 'opencv'
        logger = logging.getLogger(__name__)
        logger.warning("⚠️  picamera2 not available - fallback to OpenCV")
    except ImportError:
        logger = logging.getLogger(__name__)
        logger.error("❌ Neither picamera2 nor OpenCV available")
        CAMERA_TYPE = None

logging.basicConfig(level=config.LOG_LEVEL)


class CameraModule:
    def __init__(self):
        """Initialize the camera module with advanced processing capabilities"""
        self.camera = None
        self.is_initialized = False
        self.camera_type = CAMERA_TYPE
        self.cap = None  # For OpenCV camera
        
        # Image processing settings
        self.auto_exposure = True
        self.auto_white_balance = True
        self.image_enhancement = True
        self.noise_reduction = True
        
        # Capture statistics
        self.capture_count = 0
        self.last_capture_time = 0
        
        # Quality settings
        self.jpeg_quality = 95
        self.brightness_adjust = 0  # -100 to 100
        self.contrast_adjust = 1.0  # 0.5 to 2.0
        self.saturation_adjust = 1.0  # 0.0 to 2.0
        
    def initialize(self):
        """Initialize and configure the camera with optimal settings"""
        if not self.camera_type:
            logger.error("No camera library available (install picamera2 or opencv)")
            return False
            
        try:
            if self.camera_type == 'picamera2':
                return self._initialize_picamera2()
            elif self.camera_type == 'opencv':
                return self._initialize_opencv()
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            return False
    
    def _initialize_picamera2(self):
        """Initialize Raspberry Pi camera with advanced controls"""
        logger.info("Initializing Raspberry Pi camera (picamera2) with advanced settings...")
        
        try:
            self.camera = Picamera2()
            
            # Get camera properties safely
            try:
                # Try different ways to get camera info
                if hasattr(self.camera, 'sensor_properties'):
                    camera_props = self.camera.sensor_properties
                    logger.info(f"Camera sensor: {camera_props}")
                elif hasattr(self.camera, 'camera_properties'):
                    camera_props = self.camera.camera_properties
                    logger.info(f"Camera properties: {camera_props}")
                else:
                    logger.info("Camera properties not available - using defaults")
            except Exception as e:
                logger.debug(f"Could not get camera properties: {e}")
            
            # Configure camera for high-quality image capture with basic settings
            try:
                camera_config = self.camera.create_still_configuration(
                    main={"size": config.CAMERA_RESOLUTION, "format": config.CAMERA_FORMAT},
                    buffer_count=2,  # Double buffering for smoother capture
                )
                
                # Try to apply advanced camera controls (may not be supported)
                try:
                    if hasattr(self.camera, 'set_controls'):
                        # Basic controls that should work on most cameras
                        controls_dict = {
                            # Only include controls that are commonly available
                        }
                        # Apply controls after camera start
                    else:
                        logger.debug("Camera controls not available")
                except Exception as e:
                    logger.debug(f"Advanced camera controls not supported: {e}")
                
                self.camera.configure(camera_config)
                
                # Start camera
                self.camera.start()
                logger.info("Camera started successfully")
                
            except Exception as e:
                logger.error(f"Camera configuration failed: {e}")
                return False
            
            # Advanced warm-up with safer test captures
            logger.info(f"Camera warming up for {config.CAMERA_WARMUP_TIME} seconds...")
            time.sleep(config.CAMERA_WARMUP_TIME)
            
            # Test captures for auto-adjustment (safer version)
            try:
                self._perform_auto_calibration_safe()
            except Exception as e:
                logger.warning(f"Auto-calibration failed, continuing with defaults: {e}")
            
            self.is_initialized = True
            logger.info("Raspberry Pi camera initialized with advanced processing")
            return True
            
        except Exception as e:
            logger.error(f"picamera2 initialization failed: {e}")
            if hasattr(self, 'camera') and self.camera:
                try:
                    self.camera.close()
                except:
                    pass
            return False
    
    def _perform_auto_calibration_safe(self):
        """Perform safe auto-calibration for optimal image quality"""
        logger.info("Performing safe auto-calibration...")
        
        try:
            # Capture test images for calibration with error handling
            test_images = []
            successful_captures = 0
            
            for i in range(3):
                try:
                    time.sleep(0.5)
                    # Use a simpler capture method for calibration
                    test_array = self.camera.capture_array()
                    if test_array is not None and test_array.size > 0:
                        test_images.append(test_array)
                        successful_captures += 1
                except Exception as e:
                    logger.debug(f"Calibration capture {i+1} failed: {e}")
                    continue
            
            if successful_captures == 0:
                logger.warning("No successful calibration captures, using default settings")
                return
            
            # Analyze image statistics safely
            try:
                avg_brightness = np.mean([np.mean(img) for img in test_images])
                avg_contrast = np.mean([np.std(img) for img in test_images])
                
                logger.info(f"Auto-calibration: brightness={avg_brightness:.1f}, contrast={avg_contrast:.1f}")
                
                # Adjust settings based on analysis with safe limits
                if avg_brightness < 80:  # Too dark
                    self.brightness_adjust = min(20, 10)  # Conservative adjustment
                elif avg_brightness > 200:  # Too bright
                    self.brightness_adjust = max(-20, -10)  # Conservative adjustment
                
                if avg_contrast < 30:  # Low contrast
                    self.contrast_adjust = min(1.5, 1.2)  # Conservative adjustment
                    
                logger.info(f"Applied auto-calibration: brightness={self.brightness_adjust}, contrast={self.contrast_adjust:.2f}")
                
            except Exception as e:
                logger.warning(f"Image analysis failed during calibration: {e}")
                
        except Exception as e:
            logger.warning(f"Auto-calibration failed: {e}")
            
    def _initialize_opencv(self):
        """Initialize camera using OpenCV with advanced settings and error handling"""
        logger.info("Initializing camera with OpenCV (advanced mode)...")
        
        try:
            import cv2
        except ImportError:
            logger.error("OpenCV not available")
            return False
        
        # Try different camera indices with advanced configuration
        for camera_id in [0, 1, 2]:
            logger.debug(f"Trying camera index {camera_id}...")
            
            try:
                self.cap = cv2.VideoCapture(camera_id)
                
                if not self.cap.isOpened():
                    logger.debug(f"Camera {camera_id} not available")
                    continue
                
                # Set high-quality capture parameters
                width, height = config.CAMERA_RESOLUTION
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                self.cap.set(cv2.CAP_PROP_FPS, 30)  # Smooth capture
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce latency
                
                # Advanced camera controls (if supported)
                try:
                    self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Auto exposure
                    self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Auto focus
                    self.cap.set(cv2.CAP_PROP_AUTO_WB, 1)  # Auto white balance
                    self.cap.set(cv2.CAP_PROP_SATURATION, 60)  # Enhance saturation
                    self.cap.set(cv2.CAP_PROP_SHARPNESS, 60)  # Enhance sharpness
                    logger.debug("Advanced OpenCV controls applied")
                except Exception as e:
                    logger.debug(f"Some advanced OpenCV controls not supported: {e}")
                
                # Test capture to verify camera works
                ret, test_frame = self.cap.read()
                if ret and test_frame is not None and test_frame.size > 0:
                    logger.info(f"OpenCV camera {camera_id} initialized with advanced settings")
                    logger.info(f"Camera resolution: {test_frame.shape[1]}x{test_frame.shape[0]}")
                    self.is_initialized = True
                    return True
                else:
                    logger.debug(f"Camera {camera_id} test capture failed")
                    
            except Exception as e:
                logger.debug(f"Error testing camera {camera_id}: {e}")
            
            # Clean up failed camera
            if hasattr(self, 'cap') and self.cap:
                self.cap.release()
                self.cap = None
        
        logger.error("No working camera found with OpenCV")
        return False
    
    def capture_image(self, enhance=True, save_raw=False):
        """
        Capture an image with advanced processing and return it as bytes
        
        Args:
            enhance (bool): Apply image enhancement
            save_raw (bool): Also save raw unprocessed image
            
        Returns:
            bytes: Processed image data in JPEG format, or None if failed
        """
        if not self.is_initialized:
            logger.error("Camera not initialized")
            return None
        
        try:
            self.capture_count += 1
            capture_start = time.time()
            
            if self.camera_type == 'picamera2':
                result = self._capture_picamera2(enhance, save_raw)
            elif self.camera_type == 'opencv':
                result = self._capture_opencv(enhance, save_raw)
            else:
                logger.error("Unknown camera type")
                return None
            
            capture_time = time.time() - capture_start
            self.last_capture_time = capture_time
            
            if result is not None:
                logger.info(f"Image captured #{self.capture_count} in {capture_time:.3f}s, size: {len(result)} bytes")
            else:
                logger.error(f"Image capture #{self.capture_count} failed after {capture_time:.3f}s")
            
            return result
                
        except Exception as e:
            logger.error(f"Failed to capture image: {e}")
            return None
    
    def _capture_picamera2(self, enhance=True, save_raw=False):
        """Capture image using picamera2 with safe processing"""
        logger.debug("Capturing image with picamera2 (safe processing)...")
        
        try:
            # Capture high-quality image with error handling
            image_array = self.camera.capture_array()
            
            if image_array is None or image_array.size == 0:
                logger.error("Camera returned empty image array")
                return None
            
            # Save raw image if requested
            if save_raw:
                try:
                    raw_filename = f"raw_capture_{int(time.time())}.jpg"
                    raw_image = Image.fromarray(image_array)
                    raw_image.save(raw_filename)
                    logger.debug(f"Raw image saved: {raw_filename}")
                except Exception as e:
                    logger.warning(f"Could not save raw image: {e}")
            
            # Convert to PIL Image for processing
            try:
                image = Image.fromarray(image_array)
            except Exception as e:
                logger.error(f"Failed to convert array to PIL image: {e}")
                return None
            
            # Apply advanced image processing
            if enhance and self.image_enhancement:
                try:
                    image = self._enhance_image(image)
                except Exception as e:
                    logger.warning(f"Image enhancement failed, using original: {e}")
            
            # Convert to optimized JPEG
            try:
                buffer = BytesIO()
                image.save(buffer, format='JPEG', quality=self.jpeg_quality, optimize=True)
                image_bytes = buffer.getvalue()
                
                if len(image_bytes) == 0:
                    logger.error("JPEG conversion resulted in empty data")
                    return None
                
                logger.debug(f"Processed image: {len(image_bytes)} bytes, quality={self.jpeg_quality}%")
                return image_bytes
                
            except Exception as e:
                logger.error(f"JPEG conversion failed: {e}")
                return None
                
        except Exception as e:
            logger.error(f"picamera2 capture failed: {e}")
            return None
    
    def _capture_opencv(self, enhance=True, save_raw=False):
        """Capture image using OpenCV with advanced processing"""
        import cv2
        logger.debug("Capturing image with OpenCV (advanced processing)...")
        
        # Capture multiple frames and select the best
        best_frame = None
        best_score = 0
        
        for i in range(3):  # Capture 3 frames
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            # Calculate image quality score (using Laplacian variance)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            if score > best_score:
                best_score = score
                best_frame = frame.copy()
        
        if best_frame is None:
            logger.error("Failed to capture any frame")
            return None
        
        # Save raw frame if requested
        if save_raw:
            raw_filename = f"raw_capture_opencv_{int(time.time())}.jpg"
            cv2.imwrite(raw_filename, best_frame)
            logger.debug(f"Raw frame saved: {raw_filename}")
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(best_frame, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        image = Image.fromarray(frame_rgb)
        
        # Apply advanced image processing
        if enhance and self.image_enhancement:
            image = self._enhance_image(image)
        
        # Convert to optimized JPEG
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=self.jpeg_quality, optimize=True)
        image_bytes = buffer.getvalue()
        
        logger.debug(f"Processed OpenCV image: {len(image_bytes)} bytes, focus_score={best_score:.1f}")
        return image_bytes
    
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
            if self.camera_type == 'picamera2':
                self.camera.capture_file(filename)
            elif self.camera_type == 'opencv':
                ret, frame = self.cap.read()
                if ret:
                    import cv2
                    cv2.imwrite(filename, frame)
                else:
                    return False
            
            logger.info(f"Image saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            return False
    
    def cleanup(self):
        """Clean up camera resources"""
        try:
            if self.camera_type == 'picamera2' and self.camera:
                self.camera.stop()
                self.camera.close()
            elif self.camera_type == 'opencv' and self.cap:
                self.cap.release()
            
            self.is_initialized = False
            logger.info("Camera cleaned up")
        except Exception as e:
            logger.error(f"Error during camera cleanup: {e}")

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
        if self.camera:
            logger.info("Stopping camera...")
            self.camera.stop()
            self.camera.close()
            self.is_initialized = False
            logger.info("Camera stopped")


# Test function with advanced features
if __name__ == "__main__":
    print("="*50)
    print("🧪 TESTING ADVANCED CAMERA MODULE")
    print("="*50)
    
    cam = CameraModule()
    
    if cam.initialize():
        print("✅ Camera initialized successfully")
        print(f"📷 Camera type: {cam.camera_type}")
        
        # Test basic capture
        print("\n🔍 Testing basic capture...")
        image_data = cam.capture_image()
        if image_data:
            print(f"✅ Captured image: {len(image_data)} bytes")
            
            # Save test image
            with open("test_capture_basic.jpg", "wb") as f:
                f.write(image_data)
            print("💾 Saved as test_capture_basic.jpg")
        
        # Test enhanced capture
        print("\n🎨 Testing enhanced capture...")
        cam.set_camera_settings(brightness=10, contrast=1.2, saturation=1.1, quality=98)
        enhanced_data = cam.capture_image(enhance=True, save_raw=True)
        if enhanced_data:
            print(f"✅ Enhanced image: {len(enhanced_data)} bytes")
            with open("test_capture_enhanced.jpg", "wb") as f:
                f.write(enhanced_data)
            print("💾 Saved as test_capture_enhanced.jpg")
        
        # Test burst mode
        print("\n📸 Testing burst mode...")
        burst_images = cam.capture_burst(count=3, delay=0.3)
        print(f"✅ Burst capture: {len(burst_images)} images")
        for i, img_data in enumerate(burst_images):
            with open(f"test_burst_{i+1}.jpg", "wb") as f:
                f.write(img_data)
        
        # Show statistics
        print("\n📊 Camera statistics:")
        stats = cam.get_camera_stats()
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {key}: {value}")
        
        cam.cleanup()
        print("\n🧹 Camera cleaned up")
        print("="*50)
        print("🎉 ALL TESTS COMPLETED!")
    else:
        print("❌ Failed to initialize camera")
        print("💡 Try: sudo python3 camera_module.py")
