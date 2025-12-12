"""
Hardware Control API
Allows web dashboard to remotely control Raspberry Pi hardware
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import logging
import httpx
import config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/hardware", tags=["Hardware Control"])

# Raspberry Pi connection - use Tailscale IP (recommended)
# Get Pi IP with: tailscale ip -4
RASPBERRY_PI_HOST = "http://100.64.1.3:5000"  # Tailscale IP of Raspberry Pi



# Request models
class ConveyorSpeedRequest(BaseModel):
    speed: int  # 0-100

class ServoMoveRequest(BaseModel):
    position: str  # 'left', 'center', 'right'
    
class TriggerModeRequest(BaseModel):
    mode: str  # 'ir_sensor', 'time_based', 'continuous', 'manual'


# Admin authentication (simplified - will use Firebase later)
async def verify_admin(authorization: Optional[str] = Header(None)):
    """
    Verify admin authorization
    In production, this will check Firebase token
    """
    # TODO: Implement Firebase token verification
    # For now, just check if header exists
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True


@router.post("/conveyor/start")
async def start_conveyor(is_admin: bool = Depends(verify_admin)):
    """Start conveyor belt (Admin only)"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{RASPBERRY_PI_HOST}/control/conveyor/start", timeout=5.0)
            response.raise_for_status()
            return {"status": "success", "message": "Conveyor started"}
    except httpx.RequestError as e:
        logger.error(f"Failed to start conveyor: {e}")
        raise HTTPException(status_code=503, detail="Raspberry Pi unreachable")
    except Exception as e:
        logger.error(f"Error starting conveyor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conveyor/stop")
async def stop_conveyor(is_admin: bool = Depends(verify_admin)):
    """Stop conveyor belt (Admin only)"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{RASPBERRY_PI_HOST}/control/conveyor/stop", timeout=5.0)
            response.raise_for_status()
            return {"status": "success", "message": "Conveyor stopped"}
    except httpx.RequestError as e:
        logger.error(f"Failed to stop conveyor: {e}")
        raise HTTPException(status_code=503, detail="Raspberry Pi unreachable")
    except Exception as e:
        logger.error(f"Error stopping conveyor: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conveyor/speed")
async def set_conveyor_speed(request: ConveyorSpeedRequest, is_admin: bool = Depends(verify_admin)):
    """Set conveyor speed (Admin only)"""
    if not 0 <= request.speed <= 100:
        raise HTTPException(status_code=400, detail="Speed must be between 0-100")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{RASPBERRY_PI_HOST}/control/conveyor/speed",
                json={"speed": request.speed},
                timeout=5.0
            )
            response.raise_for_status()
            return {"status": "success", "speed": request.speed}
    except httpx.RequestError as e:
        logger.error(f"Failed to set speed: {e}")
        raise HTTPException(status_code=503, detail="Raspberry Pi unreachable")
    except Exception as e:
        logger.error(f"Error setting speed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/servo/move")
async def move_servo(request: ServoMoveRequest, is_admin: bool = Depends(verify_admin)):
    """Move servo to position (Admin only)"""
    valid_positions = ['left', 'center', 'right']
    if request.position not in valid_positions:
        raise HTTPException(status_code=400, detail=f"Position must be one of: {valid_positions}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{RASPBERRY_PI_HOST}/control/servo/move",
                json={"position": request.position},
                timeout=5.0
            )
            response.raise_for_status()
            return {"status": "success", "position": request.position}
    except httpx.RequestError as e:
        logger.error(f"Failed to move servo: {e}")
        raise HTTPException(status_code=503, detail="Raspberry Pi unreachable")
    except Exception as e:
        logger.error(f"Error moving servo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/camera/capture")
async def capture_image(is_admin: bool = Depends(verify_admin)):
    """Manually trigger image capture (Admin only)"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{RASPBERRY_PI_HOST}/control/capture", timeout=10.0)
            response.raise_for_status()
            return {"status": "success", "message": "Image captured"}
    except httpx.RequestError as e:
        logger.error(f"Failed to capture image: {e}")
        raise HTTPException(status_code=503, detail="Raspberry Pi unreachable")
    except Exception as e:
        logger.error(f"Error capturing image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger-mode")
async def set_trigger_mode(request: TriggerModeRequest, is_admin: bool = Depends(verify_admin)):
    """Change trigger mode (Admin only)"""
    valid_modes = ['ir_sensor', 'time_based', 'continuous', 'manual']
    if request.mode not in valid_modes:
        raise HTTPException(status_code=400, detail=f"Mode must be one of: {valid_modes}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{RASPBERRY_PI_HOST}/control/trigger-mode",
                json={"mode": request.mode},
                timeout=5.0
            )
            response.raise_for_status()
            return {"status": "success", "mode": request.mode}
    except httpx.RequestError as e:
        logger.error(f"Failed to set trigger mode: {e}")
        raise HTTPException(status_code=503, detail="Raspberry Pi unreachable")
    except Exception as e:
        logger.error(f"Error setting trigger mode: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/emergency-stop")
async def emergency_stop(is_admin: bool = Depends(verify_admin)):
    """Emergency stop all systems (Admin only)"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{RASPBERRY_PI_HOST}/control/emergency-stop", timeout=5.0)
            response.raise_for_status()
            return {"status": "success", "message": "Emergency stop activated"}
    except httpx.RequestError as e:
        logger.error(f"Failed emergency stop: {e}")
        raise HTTPException(status_code=503, detail="Raspberry Pi unreachable")
    except Exception as e:
        logger.error(f"Error in emergency stop: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_hardware_status():
    """Get current hardware status"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{RASPBERRY_PI_HOST}/status", timeout=5.0)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        logger.error(f"Failed to get status: {e}")
        return {
            "status": "offline",
            "message": "Raspberry Pi unreachable"
        }
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
