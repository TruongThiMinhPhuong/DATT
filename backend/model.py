"""
AI Model for Fruit Classification
Uses MobileNetV2 with transfer learning for efficient inference
"""
import logging
import numpy as np
from PIL import Image
import tensorflow as tf
from io import BytesIO
import os
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class FruitClassifier:
    def __init__(self, model_path=None):
        """
        Initialize the classifier
        
        Args:
            model_path (str): Path to trained model file
        """
        self.model_path = model_path or config.MODEL_PATH
        self.model = None
        self.classes = config.MODEL_CLASSES
        self.input_size = config.MODEL_INPUT_SIZE
        
    def load_model(self):
        """Load the trained model"""
        try:
            if os.path.exists(self.model_path):
                logger.info(f"Loading model from {self.model_path}")
                self.model = tf.keras.models.load_model(self.model_path)
                logger.info("Model loaded successfully")
            else:
                logger.warning(f"Model file not found at {self.model_path}")
                logger.info("Creating demo model for testing...")
                self.create_demo_model()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            logger.info("Creating demo model for testing...")
            self.create_demo_model()
            return True
    
    def create_demo_model(self):
        """Create a simple demo model for testing purposes"""
        logger.info("Creating demo MobileNetV2-based model...")
        
        # Create base model
        base_model = tf.keras.applications.MobileNetV2(
            input_shape=(*self.input_size, 3),
            include_top=False,
            weights='imagenet'
        )
        base_model.trainable = False
        
        # Add classification head
        inputs = tf.keras.Input(shape=(*self.input_size, 3))
        x = base_model(inputs, training=False)
        x = tf.keras.layers.GlobalAveragePooling2D()(x)
        x = tf.keras.layers.Dropout(0.2)(x)
        outputs = tf.keras.layers.Dense(len(self.classes), activation='softmax')(x)
        
        self.model = tf.keras.Model(inputs, outputs)
        
        logger.info("Demo model created successfully")
        logger.warning("⚠️  Using untrained demo model - predictions will be random!")
        logger.info("To use a trained model, place it at: " + self.model_path)
    
    def preprocess_image(self, image_bytes):
        """
        Enhanced image preprocessing for better classification accuracy
        
        Args:
            image_bytes (bytes): Raw image bytes
            
        Returns:
            np.ndarray: Preprocessed image array
        """
        try:
            import cv2
            
            # Load image
            image = Image.open(BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array for OpenCV processing
            image_array = np.array(image)
            
            # Apply advanced preprocessing
            # 1. Denoise to reduce camera noise
            image_array = cv2.fastNlMeansDenoisingColored(image_array, None, 10, 10, 7, 21)
            
            # 2. Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
            lab = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            lab = cv2.merge([l, a, b])
            image_array = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
            
            # 3. Sharpen image for better edge detection
            kernel_sharpening = np.array([[-1, -1, -1],
                                         [-1,  9, -1],
                                         [-1, -1, -1]])
            image_array = cv2.filter2D(image_array, -1, kernel_sharpening * 0.5)
            
            # 4. Color balance to correct lighting variations
            image_array = self._auto_color_balance(image_array)
            
            # Resize to model input size
            image_array = cv2.resize(image_array, self.input_size, interpolation=cv2.INTER_LANCZOS4)
            
            # Normalize to [0, 1]
            image_array = image_array.astype(np.float32) / 255.0
            
            # Add batch dimension
            image_array = np.expand_dims(image_array, axis=0)
            
            logger.debug("Image preprocessing complete with enhancements")
            return image_array
            
        except Exception as e:
            logger.error(f"Failed to preprocess image: {e}")
            return None
    
    def _auto_color_balance(self, image):
        """
        Automatic color balance to correct lighting
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            np.ndarray: Color-balanced image
        """
        result = np.zeros_like(image)
        for i in range(3):  # Process each color channel
            hist, bins = np.histogram(image[:, :, i].flatten(), 256, [0, 256])
            cdf = hist.cumsum()
            cdf_normalized = cdf * hist.max() / cdf.max()
            
            # Find 1% and 99% percentiles
            total_pixels = image.shape[0] * image.shape[1]
            low_thresh = np.searchsorted(cdf, total_pixels * 0.01)
            high_thresh = np.searchsorted(cdf, total_pixels * 0.99)
            
            # Stretch histogram
            result[:, :, i] = np.clip((image[:, :, i] - low_thresh) * 255.0 / (high_thresh - low_thresh), 0, 255)
        
        return result.astype(np.uint8)
    
    def classify(self, image_bytes):
        """
        Enhanced classification with detailed quality metrics
        
        Args:
            image_bytes (bytes): Raw image bytes
            
        Returns:
            dict: Detailed classification result
        """
        if self.model is None:
            logger.error("Model not loaded")
            return {
                'classification': config.MODEL_CLASSES[2],  # 'other'
                'confidence': 0.0,
                'all_probabilities': {},
                'quality_score': 0.0,
                'recommendation': 'Model not loaded'
            }
        
        try:
            # Assess image quality
            quality_metrics = self._assess_image_quality(image_bytes)
            
            # Preprocess image
            image_array = self.preprocess_image(image_bytes)
            if image_array is None:
                raise ValueError("Failed to preprocess image")
            
            # Make prediction
            predictions = self.model.predict(image_array, verbose=0)
            probabilities = predictions[0]
            
            # Get top prediction
            top_index = np.argmax(probabilities)
            top_class = self.classes[top_index]
            confidence = float(probabilities[top_index])
            
            # Get second best for comparison
            sorted_indices = np.argsort(probabilities)[::-1]
            second_confidence = float(probabilities[sorted_indices[1]])
            confidence_gap = confidence - second_confidence
            
            # Get all probabilities
            all_probs = {
                class_name: float(prob)
                for class_name, prob in zip(self.classes, probabilities)
            }
            
            # Calculate quality score (0-100)
            quality_score = (
                confidence * 50 +  # Prediction confidence
                confidence_gap * 30 +  # Gap to second best
                quality_metrics['overall'] * 20  # Image quality
            )
            
            # Generate recommendation
            recommendation = self._generate_recommendation(confidence, quality_score, quality_metrics)
            
            logger.info(f"Classification: {top_class} ({confidence:.2%}), Quality: {quality_score:.1f}")
            
            return {
                'classification': top_class,
                'confidence': confidence,
                'all_probabilities': all_probs,
                'quality_score': quality_score,
                'confidence_gap': confidence_gap,
                'image_quality': quality_metrics,
                'recommendation': recommendation
            }
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return {
                'classification': config.MODEL_CLASSES[2],  # 'other'
                'confidence': 0.0,
                'all_probabilities': {}
            }
    
    def save_model(self, path=None):
        """Save the model to disk"""
        if self.model is None:
            logger.error("No model to save")
            return False
        
        save_path = path or self.model_path
        
        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            self.model.save(save_path)
            logger.info(f"Model saved to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False

    
    def _assess_image_quality(self, image_bytes):
        """
        Assess image quality metrics
        
        Args:
            image_bytes (bytes): Raw image bytes
            
        Returns:
            dict: Quality metrics
        """
        try:
            import cv2
            
            # Load image
            image = Image.open(BytesIO(image_bytes))
            image_array = np.array(image.convert('RGB'))
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            
            # 1. Brightness (0-1, optimal around 0.4-0.6)
            brightness = np.mean(gray) / 255.0
            brightness_score = 1.0 - abs(brightness - 0.5) * 2
            
            # 2. Sharpness using Laplacian variance
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = np.var(laplacian)
            sharpness_score = min(sharpness / 500.0, 1.0)  # Normalize
            
            # 3. Blur detection
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            blur_score = min(blur_score / 500.0, 1.0)
            
            # 4. Contrast
            contrast = gray.std() / 128.0
            contrast_score = min(contrast, 1.0)
            
            # Overall quality (weighted average)
            overall = (
                brightness_score * 0.25 +
                sharpness_score * 0.35 +
                blur_score * 0.25 +
                contrast_score * 0.15
            )
            
            return {
                'brightness': brightness_score,
                'sharpness': sharpness_score,
                'blur': blur_score,
                'contrast': contrast_score,
                'overall': overall
            }
            
        except Exception as e:
            logger.error(f"Failed to assess image quality: {e}")
            return {
                'brightness': 0.5,
                'sharpness': 0.5,
                'blur': 0.5,
                'contrast': 0.5,
                'overall': 0.5
            }
    
    def _generate_recommendation(self, confidence, quality_score, quality_metrics):
        """
        Generate recommendation based on classification results
        
        Args:
            confidence (float): Classification confidence
            quality_score (float): Overall quality score
            quality_metrics (dict): Detailed quality metrics
            
        Returns:
            str: Recommendation message
        """
        recommendations = []
        
        # Check confidence
        if confidence < 0.6:
            recommendations.append("⚠️ Low confidence - verify result manually")
        elif confidence < 0.8:
            recommendations.append("⚡ Medium confidence - acceptable")
        else:
            recommendations.append("✅ High confidence - reliable result")
        
        # Check image quality
        if quality_metrics['brightness'] < 0.5:
            recommendations.append("💡 Improve lighting - image too dark")
        elif quality_metrics['brightness'] > 0.8:
            recommendations.append("☀️ Reduce lighting - image too bright")
        
        if quality_metrics['sharpness'] < 0.5:
            recommendations.append("🔍 Improve focus - image not sharp")
        
        if quality_metrics['blur'] < 0.5:
            recommendations.append("📹 Reduce motion blur - stabilize camera")
        
        if quality_metrics['contrast'] < 0.4:
            recommendations.append("🎨 Low contrast - adjust camera settings")
        
        # Overall assessment
        if quality_score > 80:
            recommendations.append("🌟 Excellent quality")
        elif quality_score > 60:
            recommendations.append("👍 Good quality")
        elif quality_score > 40:
            recommendations.append("⚠️ Fair quality - improvements needed")
        else:
            recommendations.append("❌ Poor quality - check camera setup")
        
        return " | ".join(recommendations)


# Global classifier instance
classifier = FruitClassifier()


# Test function
if __name__ == "__main__":
    print("Testing Fruit Classifier...")
    
    # Load model
    classifier.load_model()
    
    # Create test image
    from PIL import Image
    import io
    
    test_image = Image.new('RGB', (224, 224), color='red')
    img_bytes = io.BytesIO()
    test_image.save(img_bytes, format='JPEG')
    img_bytes = img_bytes.getvalue()
    
    # Test classification
    result = classifier.classify(img_bytes)
    print(f"Result: {result}")
