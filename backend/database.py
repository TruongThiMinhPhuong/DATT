"""
Database module for storing classification results
Uses SQLite for simplicity
"""
import aiosqlite
import logging
import os
from datetime import datetime
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path=None):
        """Initialize database connection"""
        self.db_path = db_path or config.DATABASE_PATH
        self.connection = None
        
    async def initialize(self):
        """Create database and tables if they don't exist"""
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Connect to database
            self.connection = await aiosqlite.connect(self.db_path)
            
            # Create classifications table
            await self.connection.execute('''
                CREATE TABLE IF NOT EXISTS classifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    classification TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    device_id TEXT,
                    processing_time REAL,
                    image_url TEXT,
                    image_path TEXT,
                    supabase_id TEXT,
                    synced_to_cloud BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index on timestamp
            await self.connection.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON classifications(timestamp)
            ''')
            
            await self.connection.commit()
            logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def insert_classification(self, classification, confidence, 
                                   device_id=None, timestamp=None, 
                                   processing_time=None, image_url=None,
                                   image_path=None, supabase_id=None):
        """
        Insert classification result into database
        
        Args:
            classification (str): Classification category
            confidence (float): Confidence score
            device_id (str): Device identifier
            timestamp (float): Unix timestamp
            processing_time (float): Processing time in seconds
            image_url (str): Supabase Storage URL
            image_path (str): Local/cloud file path
            supabase_id (str): Supabase record ID
        """
        try:
            if timestamp is None:
                timestamp = datetime.now().timestamp()
            
            await self.connection.execute('''
                INSERT INTO classifications 
                (timestamp, classification, confidence, device_id, processing_time,
                 image_url, image_path, supabase_id, synced_to_cloud)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (timestamp, classification, confidence, device_id, processing_time,
                  image_url, image_path, supabase_id, 1 if supabase_id else 0))
            
            await self.connection.commit()
            logger.debug(f"Inserted classification: {classification} ({confidence:.2%})")
            
        except Exception as e:
            logger.error(f"Failed to insert classification: {e}")
    
    async def get_recent_classifications(self, limit=100):
        """
        Get recent classification results
        
        Args:
            limit (int): Maximum number of results
            
        Returns:
            list: List of classification records
        """
        try:
            cursor = await self.connection.execute('''
                SELECT id, timestamp, classification, confidence, 
                       device_id, processing_time, created_at
                FROM classifications
                ORDER BY id DESC
                LIMIT ?
            ''', (limit,))
            
            rows = await cursor.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'classification': row[2],
                    'confidence': row[3],
                    'device_id': row[4],
                    'processing_time': row[5],
                    'created_at': row[6]
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get classifications: {e}")
            return []
    
    async def get_statistics(self):
        """
        Get classification statistics
        
        Returns:
            dict: Statistics including counts and averages
        """
        try:
            # Total count
            cursor = await self.connection.execute(
                'SELECT COUNT(*) FROM classifications'
            )
            total = (await cursor.fetchone())[0]
            
            # Count by category
            cursor = await self.connection.execute('''
                SELECT classification, COUNT(*) as count
                FROM classifications
                GROUP BY classification
            ''')
            category_counts = {}
            async for row in cursor:
                category_counts[row[0]] = row[1]
            
            # Average confidence
            cursor = await self.connection.execute(
                'SELECT AVG(confidence) FROM classifications'
            )
            avg_confidence = (await cursor.fetchone())[0] or 0.0
            
            # Average processing time
            cursor = await self.connection.execute('''
                SELECT AVG(processing_time) 
                FROM classifications 
                WHERE processing_time IS NOT NULL
            ''')
            avg_processing_time = (await cursor.fetchone())[0] or 0.0
            
            return {
                'total': total,
                'category_counts': category_counts,
                'avg_confidence': avg_confidence,
                'avg_processing_time': avg_processing_time
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {
                'total': 0,
                'category_counts': {},
                'avg_confidence': 0.0,
                'avg_processing_time': 0.0
            }
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            logger.info("Database connection closed")


# Global database instance
db = Database()
