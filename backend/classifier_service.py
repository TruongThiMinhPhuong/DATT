"""
Classifier Service - Background service for processing images
Consumes images from RabbitMQ, runs classification, and publishes results
"""
import json
import logging
import time
import threading
import pika
from pika.exceptions import AMQPConnectionError
from model import classifier
from database import db
import config
import asyncio

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class ClassifierService:
    def __init__(self):
        """Initialize classifier service"""
        self.connection = None
        self.channel = None
        self.is_running = False
        self.is_connected = False
        
    def connect(self):
        """Connect to RabbitMQ"""
        try:
            logger.info(f"Connecting to RabbitMQ at {config.RABBITMQ_HOST}:{config.RABBITMQ_PORT}")
            
            credentials = pika.PlainCredentials(
                config.RABBITMQ_USER,
                config.RABBITMQ_PASSWORD
            )
            
            parameters = pika.ConnectionParameters(
                host=config.RABBITMQ_HOST,
                port=config.RABBITMQ_PORT,
                virtual_host=config.RABBITMQ_VHOST,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queues
            self.channel.queue_declare(queue=config.IMAGE_QUEUE, durable=True)
            self.channel.queue_declare(queue=config.RESULT_QUEUE, durable=True)
            
            # Set QoS
            self.channel.basic_qos(prefetch_count=config.PREFETCH_COUNT)
            
            self.is_connected = True
            logger.info("Connected to RabbitMQ")
            return True
            
        except AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
    
    def process_image(self, ch, method, properties, body):
        """
        Process incoming image message
        
        Args:
            ch: Channel
            method: Delivery method
            properties: Message properties
            body: Message body
        """
        start_time = time.time()
        
        try:
            # Parse message
            message = json.loads(body)
            image_hex = message.get('image')
            metadata = message.get('metadata', {})
            
            logger.info(f"Processing image from {metadata.get('device_id', 'unknown')}")
            
            # Convert hex string back to bytes
            image_bytes = bytes.fromhex(image_hex)
            
            # Classify image
            result = classifier.classify(image_bytes)
            
            # Add metadata
            result['metadata'] = metadata
            result['processing_time'] = time.time() - start_time
            
            # Store in database (async)
            asyncio.run(db.insert_classification(
                classification=result['classification'],
                confidence=result['confidence'],
                device_id=metadata.get('device_id'),
                timestamp=metadata.get('timestamp'),
                processing_time=result['processing_time']
            ))
            
            # Publish result
            result_json = json.dumps(result)
            self.channel.basic_publish(
                exchange='',
                routing_key=config.RESULT_QUEUE,
                body=result_json,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            
            logger.info(f"Result published: {result['classification']} "
                       f"({result['confidence']:.2%}) in {result['processing_time']:.3f}s")
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            # Reject message without requeue
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def start(self):
        """Start the classifier service"""
        logger.info("=== Starting Classifier Service ===")
        
        # Initialize database
        asyncio.run(db.initialize())
        
        # Load AI model
        logger.info("Loading AI model...")
        if not classifier.load_model():
            logger.error("Failed to load model")
            return False
        
        # Connect to RabbitMQ
        if not self.connect():
            logger.error("Failed to connect to RabbitMQ")
            return False
        
        # Start consuming
        logger.info("Starting to consume messages...")
        self.is_running = True
        
        self.channel.basic_consume(
            queue=config.IMAGE_QUEUE,
            on_message_callback=self.process_image
        )
        
        logger.info("=== Classifier Service Running ===")
        logger.info(f"Waiting for images on queue: {config.IMAGE_QUEUE}")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Service interrupted by user")
            self.stop()
        except Exception as e:
            logger.error(f"Error in consume loop: {e}")
            self.stop()
    
    def stop(self):
        """Stop the classifier service"""
        logger.info("Stopping classifier service...")
        self.is_running = False
        
        if self.channel:
            self.channel.stop_consuming()
        
        if self.connection:
            self.connection.close()
        
        asyncio.run(db.close())
        
        logger.info("Classifier service stopped")


def main():
    """Main entry point"""
    service = ClassifierService()
    service.start()


if __name__ == "__main__":
    main()
