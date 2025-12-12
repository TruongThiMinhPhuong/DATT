"""
Supabase Storage Integration
Handles image uploads to Supabase Storage and Database
"""
import logging
import os
from datetime import datetime
from supabase import create_client, Client
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class SupabaseStorage:
    def __init__(self):
        """Initialize Supabase connection"""
        self.supabase: Client = None
        self.initialized = False
        
    def initialize(self):
        """Initialize Supabase client"""
        try:
            supabase_url = config.SUPABASE_URL
            supabase_key = config.SUPABASE_KEY
            
            if not supabase_url or not supabase_key:
                logger.warning("Supabase credentials not configured")
                logger.warning("Cloud storage features will be disabled")
                return False
            
            # Initialize Supabase client
            self.supabase = create_client(supabase_url, supabase_key)
            
            self.initialized = True
            logger.info(f"Supabase connected: {supabase_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase: {e}")
            return False
    
    async def upload_image(self, image_bytes, classification, confidence, 
                          device_id=None, timestamp=None):
        """
        Upload image to Supabase Storage and metadata to Database
        
        Args:
            image_bytes (bytes): Image data
            classification (str): Classification result
            confidence (float): Confidence score
            device_id (str): Device identifier
            timestamp (float): Unix timestamp
            
        Returns:
            dict: {
                'image_url': str,
                'record_id': str,
                'success': bool
            }
        """
        if not self.initialized:
            logger.warning("Supabase not initialized, skipping upload")
            return {'success': False}
        
        try:
            if timestamp is None:
                timestamp = datetime.now().timestamp()
            
            # Generate unique filename
            dt = datetime.fromtimestamp(timestamp)
            filename = f"{dt.strftime('%Y%m%d_%H%M%S')}_{classification}.jpg"
            blob_path = f"images/{filename}"
            
            # Upload to Supabase Storage
            result = self.supabase.storage.from_('fruit-images').upload(
                blob_path,
                image_bytes,
                file_options={"content-type": "image/jpeg"}
            )
            
            # Get public URL
            image_url = self.supabase.storage.from_('fruit-images').get_public_url(blob_path)
            
            logger.info(f"Image uploaded: {filename}")
            
            # Store metadata in Supabase Database
            insert_result = self.supabase.table('classifications').insert({
                'timestamp': datetime.fromtimestamp(timestamp).isoformat(),
                'classification': classification,
                'confidence': confidence,
                'device_id': device_id,
                'image_url': image_url,
                'image_path': blob_path
            }).execute()
            
            record_id = insert_result.data[0]['id'] if insert_result.data else None
            logger.info(f"Metadata stored in Supabase: {record_id}")
            
            return {
                'success': True,
                'image_url': image_url,
                'record_id': record_id,
                'blob_path': blob_path
            }
            
        except Exception as e:
            logger.error(f"Failed to upload to Supabase: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_recent_images(self, limit=20):
        """
        Get recent images from Supabase Database
        
        Args:
            limit (int): Maximum number of results
            
        Returns:
            list: List of classification documents
        """
        if not self.initialized:
            return []
        
        try:
            result = self.supabase.table('classifications') \
                .select('*') \
                .order('timestamp', desc=True) \
                .limit(limit) \
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Failed to get recent images: {e}")
            return []
    
    async def get_statistics(self):
        """
        Get statistics from Supabase Database
        
        Returns:
            dict: Statistics summary
        """
        if not self.initialized:
            return {}
        
        try:
            # Get all classifications
            result = self.supabase.table('classifications').select('*').execute()
            
            total = 0
            category_counts = {}
            confidence_sum = 0
            
            for doc in result.data:
                total += 1
                
                # Count by category
                classification = doc.get('classification', 'unknown')
                category_counts[classification] = category_counts.get(classification, 0) + 1
                
                # Sum confidence
                confidence_sum += doc.get('confidence', 0)
            
            avg_confidence = confidence_sum / total if total > 0 else 0
            
            return {
                'total': total,
                'category_counts': category_counts,
                'avg_confidence': avg_confidence
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def check_user_role(self, user_id):
        """
        Check if user is admin
        
        Args:
            user_id (str): Supabase user ID
            
        Returns:
            str: User role ('admin', 'viewer', or None)
        """
        if not self.initialized:
            return None
        
        try:
            result = self.supabase.table('users').select('role').eq('id', user_id).execute()
            if result.data:
                return result.data[0].get('role', 'viewer')
            return None
            
        except Exception as e:
            logger.error(f"Failed to check user role: {e}")
            return None
    
    async def delete_image(self, image_path, record_id):
        """
        Delete image from storage and database
        
        Args:
            image_path (str): Path to image in storage
            record_id (str): Database record ID
            
        Returns:
            bool: Success status
        """
        if not self.initialized:
            return False
        
        try:
            # Delete from storage
            self.supabase.storage.from_('fruit-images').remove([image_path])
            
            # Delete from database
            self.supabase.table('classifications').delete().eq('id', record_id).execute()
            
            logger.info(f"Deleted image and record: {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete: {e}")
            return False


# Global Supabase instance
supabase_storage = SupabaseStorage()
