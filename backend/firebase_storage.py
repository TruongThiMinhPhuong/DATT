"""
Firebase Storage Integration
Handles image uploads to Firebase Cloud Storage and Firestore
"""
import firebase_admin
from firebase_admin import credentials, storage, firestore
import logging
import os
from datetime import datetime
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class FirebaseStorage:
    def __init__(self, credentials_path='firebase_config.json'):
        """Initialize Firebase connection"""
        self.credentials_path = credentials_path
        self.bucket = None
        self.db = None
        self.initialized = False
        
    def initialize(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if credentials file exists
            if not os.path.exists(self.credentials_path):
                logger.warning(f"Firebase credentials not found: {self.credentials_path}")
                logger.warning("Cloud storage features will be disabled")
                return False
            
            # Initialize Firebase Admin (only once)
            if not firebase_admin._apps:
                cred = credentials.Certificate(self.credentials_path)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': config.FIREBASE_STORAGE_BUCKET
                })
                logger.info("Firebase Admin SDK initialized")
            
            # Get Storage bucket and Firestore client
            self.bucket = storage.bucket()
            self.db = firestore.client()
            
            self.initialized = True
            logger.info(f"Firebase Storage connected: {self.bucket.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            return False
    
    async def upload_image(self, image_bytes, classification, confidence, 
                          device_id=None, timestamp=None):
        """
        Upload image to Firebase Storage and metadata to Firestore
        
        Args:
            image_bytes (bytes): Image data
            classification (str): Classification result
            confidence (float): Confidence score
            device_id (str): Device identifier
            timestamp (float): Unix timestamp
            
        Returns:
            dict: {
                'image_url': str,
                'firebase_id': str,
                'success': bool
            }
        """
        if not self.initialized:
            logger.warning("Firebase not initialized, skipping upload")
            return {'success': False}
        
        try:
            if timestamp is None:
                timestamp = datetime.now().timestamp()
            
            # Generate unique filename
            dt = datetime.fromtimestamp(timestamp)
            filename = f"{dt.strftime('%Y%m%d_%H%M%S')}_{classification}.jpg"
            blob_path = f"images/{filename}"
            
            # Upload to Storage
            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(
                image_bytes,
                content_type='image/jpeg'
            )
            
            # Make publicly accessible
            blob.make_public()
            image_url = blob.public_url
            
            logger.info(f"Image uploaded: {filename}")
            
            # Store metadata in Firestore
            doc_ref = self.db.collection('classifications').document()
            doc_ref.set({
                'timestamp': timestamp,
                'classification': classification,
                'confidence': confidence,
                'device_id': device_id,
                'image_url': image_url,
                'image_path': blob_path,
                'created_at': firestore.SERVER_TIMESTAMP
            })
            
            firebase_id = doc_ref.id
            logger.info(f"Metadata stored in Firestore: {firebase_id}")
            
            return {
                'success': True,
                'image_url': image_url,
                'firebase_id': firebase_id,
                'blob_path': blob_path
            }
            
        except Exception as e:
            logger.error(f"Failed to upload to Firebase: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_recent_images(self, limit=20):
        """
        Get recent images from Firestore
        
        Args:
            limit (int): Maximum number of results
            
        Returns:
            list: List of classification documents
        """
        if not self.initialized:
            return []
        
        try:
            docs = self.db.collection('classifications') \
                .order_by('timestamp', direction=firestore.Query.DESCENDING) \
                .limit(limit) \
                .stream()
            
            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get recent images: {e}")
            return []
    
    async def get_statistics(self):
        """
        Get statistics from Firestore
        
        Returns:
            dict: Statistics summary
        """
        if not self.initialized:
            return {}
        
        try:
            # Get all classifications
            docs = self.db.collection('classifications').stream()
            
            total = 0
            category_counts = {}
            confidence_sum = 0
            
            for doc in docs:
                data = doc.to_dict()
                total += 1
                
                # Count by category
                classification = data.get('classification', 'unknown')
                category_counts[classification] = category_counts.get(classification, 0) + 1
                
                # Sum confidence
                confidence_sum += data.get('confidence', 0)
            
            avg_confidence = confidence_sum / total if total > 0 else 0
            
            return {
                'total': total,
                'category_counts': category_counts,
                'avg_confidence': avg_confidence
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def check_user_role(self, uid):
        """
        Check if user is admin
        
        Args:
            uid (str): Firebase user UID
            
        Returns:
            str: User role ('admin', 'viewer', or None)
        """
        if not self.initialized:
            return None
        
        try:
            doc = self.db.collection('users').document(uid).get()
            if doc.exists:
                return doc.to_dict().get('role', 'viewer')
            return None
            
        except Exception as e:
            logger.error(f"Failed to check user role: {e}")
            return None


# Global Firebase instance
firebase_storage = FirebaseStorage()
