"""
Raspberry Pi Control Server
Provides HTTP API for remote hardware control from web dashboard
"""
from flask import Flask, request, jsonify
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from motor_controller import MotorController
from camera_module import CameraModule
import config as pi_config

app = Flask(__name__)
logging.basicConfig(level=pi_config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize hardware
motor = MotorController()
camera = CameraModule()
hardware_initialized = False


def initialize_hardware():
    """Initialize hardware on first request"""
    global hardware_initialized
    if not hardware_initialized:
        logger.info("Initializing hardware...")
        if motor.initialize():
            logger.info("Motor controller initialized")
        if camera.initialize():
            logger.info("Camera initialized")
        hardware_initialized = True


# Initialize on startup
with app.app_context():
    initialize_hardware()


@app.route('/status', methods=['GET'])
def get_status():
    """Get current hardware status"""
    return jsonify({
        'status': 'online',
        'hardware_initialized': hardware_initialized,
        'motor_initialized': motor.is_initialized,
        'camera_initialized': camera.is_initialized,
        'current_servo_position': motor.current_servo_angle if motor.is_initialized else None,
        'current_conveyor_speed': motor.current_conveyor_speed if motor.is_initialized else None,
        'trigger_mode': pi_config.TRIGGER_MODE
    })


@app.route('/control/conveyor/start', methods=['POST'])
def start_conveyor():
    """Start conveyor belt"""
    try:
        if not motor.is_initialized:
            return jsonify({'error': 'Motor not initialized'}), 503
        
        speed = request.json.get('speed', pi_config.CONVEYOR_SPEED) if request.json else pi_config.CONVEYOR_SPEED
        
        if motor.start_conveyor(speed):
            logger.info(f"Conveyor started at {speed}%")
            return jsonify({'status': 'success', 'speed': speed})
        else:
            return jsonify({'error': 'Failed to start conveyor'}), 500
    except Exception as e:
        logger.error(f"Error starting conveyor: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/control/conveyor/stop', methods=['POST'])
def stop_conveyor():
    """Stop conveyor belt"""
    try:
        if not motor.is_initialized:
            return jsonify({'error': 'Motor not initialized'}), 503
        
        if motor.stop_conveyor():
            logger.info("Conveyor stopped")
            return jsonify({'status': 'success'})
        else:
            return jsonify({'error': 'Failed to stop conveyor'}), 500
    except Exception as e:
        logger.error(f"Error stopping conveyor: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/control/conveyor/speed', methods=['POST'])
def set_conveyor_speed():
    """Set conveyor speed"""
    try:
        if not motor.is_initialized:
            return jsonify({'error': 'Motor not initialized'}), 503
        
        data = request.get_json()
        speed = data.get('speed')
        
        if speed is None:
            return jsonify({'error': 'Speed parameter required'}), 400
        
        if not 0 <= speed <= 100:
            return jsonify({'error': 'Speed must be between 0-100'}), 400
        
        if motor.start_conveyor(speed):
            logger.info(f"Conveyor speed set to {speed}%")
            return jsonify({'status': 'success', 'speed': speed})
        else:
            return jsonify({'error': 'Failed to set speed'}), 500
    except Exception as e:
        logger.error(f"Error setting speed: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/control/servo/move', methods=['POST'])
def move_servo():
    """Move servo to position"""
    try:
        if not motor.is_initialized:
            return jsonify({'error': 'Motor not initialized'}), 503
        
        data = request.get_json()
        position = data.get('position')
        
        if position not in ['left', 'center', 'right']:
            return jsonify({'error': 'Position must be left, center, or right'}), 400
        
        success = False
        if position == 'left':
            success = motor.set_servo_left()
        elif position == 'center':
            success = motor.set_servo_center()
        elif position == 'right':
            success = motor.set_servo_right()
        
        if success:
            logger.info(f"Servo moved to {position}")
            return jsonify({'status': 'success', 'position': position})
        else:
            return jsonify({'error': 'Failed to move servo'}), 500
    except Exception as e:
        logger.error(f"Error moving servo: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/control/capture', methods=['POST'])
def capture_image():
    """Manually capture image"""
    try:
        if not camera.is_initialized:
            return jsonify({'error': 'Camera not initialized'}), 503
        
        image_bytes = camera.capture_image()
        if image_bytes:
            logger.info("Image captured manually")
            # TODO: Send to RabbitMQ for processing
            return jsonify({
                'status': 'success',
                'message': 'Image captured and sent for classification',
                'size': len(image_bytes)
            })
        else:
            return jsonify({'error': 'Failed to capture image'}), 500
    except Exception as e:
        logger.error(f"Error capturing image: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/control/trigger-mode', methods=['POST'])
def set_trigger_mode():
    """Change trigger mode"""
    try:
        data = request.get_json()
        mode = data.get('mode')
        
        valid_modes = ['ir_sensor', 'time_based', 'continuous', 'manual']
        if mode not in valid_modes:
            return jsonify({'error': f'Mode must be one of: {valid_modes}'}), 400
        
        # Update config (in production, write to config file)
        pi_config.TRIGGER_MODE = mode
        logger.info(f"Trigger mode changed to: {mode}")
        
        return jsonify({
            'status': 'success',
            'mode': mode,
            'message': 'Mode changed. Restart main.py to apply.'
        })
    except Exception as e:
        logger.error(f"Error setting trigger mode: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/control/emergency-stop', methods=['POST'])
def emergency_stop():
    """Emergency stop all systems"""
    try:
        logger.warning("EMERGENCY STOP ACTIVATED!")
        
        if motor.is_initialized:
            motor.stop_conveyor()
            motor.set_servo_center()
        
        return jsonify({
            'status': 'success',
            'message': 'Emergency stop activated'
        })
    except Exception as e:
        logger.error(f"Error in emergency stop: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


if __name__ == '__main__':
    # Run Flask server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )
