"""
RabbitMQ Client for Raspberry Pi
Handles communication with backend server
"""
import json
import logging
import time
import threading
import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


class RabbitMQClient:
    def __init__(self, result_callback=None):
        """
        Initialize RabbitMQ client
        
        Args:
            result_callback (callable): Function to call when receiving classification results
        """
        self.connection = None
        self.channel = None
        self.result_callback = result_callback
        self.is_connected = False
        self.consumer_thread = None
        self.should_consume = False
        
    def connect(self):
        """Establish connection to RabbitMQ server"""
        try:
            logger.info(f"Connecting to RabbitMQ at {config.RABBITMQ_HOST}:{config.RABBITMQ_PORT}...")
            
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
            
            self.is_connected = True
            logger.info("Connected to RabbitMQ successfully")
            return True
            
        except AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            return False
    
    def send_image(self, image_bytes, metadata=None):
        """
        Send image to backend for classification
        
        Args:
            image_bytes (bytes): Image data in bytes
            metadata (dict): Additional metadata (timestamp, etc.)
            
        Returns:
            bool: True if sent successfully
        """
        if not self.is_connected:
            logger.error("Not connected to RabbitMQ")
            return False
        
        try:
            # Prepare message
            message = {
                'image': image_bytes.hex(),  # Convert bytes to hex string
                'metadata': metadata or {}
            }
            
            # Add timestamp if not present
            if 'timestamp' not in message['metadata']:
                message['metadata']['timestamp'] = time.time()
            
            # Serialize message
            message_json = json.dumps(message)
            
            # Publish to queue
            self.channel.basic_publish(
                exchange='',
                routing_key=config.IMAGE_QUEUE,
                body=message_json,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )
            
            logger.info(f"Image sent to queue ({len(image_bytes)} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send image: {e}")
            return False
    
    def _on_result_received(self, ch, method, properties, body):
        """Callback when classification result is received"""
        try:
            # Parse result
            result = json.loads(body)
            logger.info(f"Received classification result: {result}")
            
            # Call user callback
            if self.result_callback:
                self.result_callback(result)
            
            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error processing result: {e}")
            # Reject message
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def start_consuming_results(self):
        """Start consuming classification results in a separate thread"""
        if not self.is_connected:
            logger.error("Not connected to RabbitMQ")
            return False
        
        try:
            # Set up consumer
            self.channel.basic_qos(prefetch_count=1)
            self.channel.basic_consume(
                queue=config.RESULT_QUEUE,
                on_message_callback=self._on_result_received
            )
            
            # Start consuming in thread
            self.should_consume = True
            self.consumer_thread = threading.Thread(target=self._consume_loop, daemon=True)
            self.consumer_thread.start()
            
            logger.info("Started consuming classification results")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start consuming: {e}")
            return False
    
    def _consume_loop(self):
        """Consumption loop running in separate thread"""
        try:
            while self.should_consume:
                self.connection.process_data_events(time_limit=1)
        except Exception as e:
            logger.error(f"Error in consume loop: {e}")
            self.is_connected = False
    
    def stop_consuming(self):
        """Stop consuming messages"""
        self.should_consume = False
        if self.consumer_thread:
            self.consumer_thread.join(timeout=2)
        logger.info("Stopped consuming results")
    
    def disconnect(self):
        """Close connection to RabbitMQ"""
        if self.connection:
            try:
                self.stop_consuming()
                self.connection.close()
                self.is_connected = False
                logger.info("Disconnected from RabbitMQ")
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
    
    def reconnect(self, max_attempts=None):
        """
        Attempt to reconnect to RabbitMQ
        
        Args:
            max_attempts (int): Maximum reconnection attempts (None for infinite)
        """
        attempts = 0
        while max_attempts is None or attempts < max_attempts:
            attempts += 1
            logger.info(f"Reconnection attempt {attempts}...")
            
            if self.connect():
                if self.result_callback:
                    self.start_consuming_results()
                return True
            
            logger.warning(f"Reconnection failed, waiting {config.RETRY_DELAY} seconds...")
            time.sleep(config.RETRY_DELAY)
        
        logger.error("Max reconnection attempts reached")
        return False


# Test function
if __name__ == "__main__":
    def test_callback(result):
        print(f"Received result: {result}")
    
    print("Testing RabbitMQ Client...")
    client = RabbitMQClient(result_callback=test_callback)
    
    if client.connect():
        print("Connected successfully")
        
        # Start consuming results
        client.start_consuming_results()
        
        # Send test message
        test_image = b"test_image_data"
        if client.send_image(test_image, {'test': True}):
            print("Test message sent")
        
        # Wait for results
        print("Waiting for results (press Ctrl+C to stop)...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping...")
        
        client.disconnect()
    else:
        print("Failed to connect")
