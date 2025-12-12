"""
Backend Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'admin')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'phuong123')
RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')

# Queue Names
IMAGE_QUEUE = 'fruit_images'
RESULT_QUEUE = 'classification_results'

# Model Configuration
MODEL_PATH = os.getenv('MODEL_PATH', 'models/fruit_classifier.h5')
MODEL_INPUT_SIZE = (224, 224)  # Standard for MobileNetV2
MODEL_CLASSES = ['fresh_fruit', 'spoiled_fruit', 'other']

# Classification Thresholds
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.6))

# API Configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 8000))
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/classifications.db')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://your-project.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'your-anon-key')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', 'your-service-role-key')

# Performance
MAX_WORKERS = int(os.getenv('MAX_WORKERS', 2))
PREFETCH_COUNT = int(os.getenv('PREFETCH_COUNT', 1))
