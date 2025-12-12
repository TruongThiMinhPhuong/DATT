"""
FastAPI Backend API
Provides REST API and WebSocket for dashboard
"""
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
from typing import Set
from database import db
import config

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to websocket: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up API server...")
    await db.initialize()
    yield
    # Shutdown
    logger.info("Shutting down API server...")
    await db.close()


# Create FastAPI app
app = FastAPI(
    title="Fruit Classification API",
    description="API for AI-powered fruit sorting system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include hardware control router
try:
    from hardware_api import router as hardware_router
    app.include_router(hardware_router)
    logger.info("Hardware control API enabled")
except ImportError:
    logger.warning("Hardware API not available - hardware_api.py not found")



@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Fruit Classification API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": asyncio.get_event_loop().time()
    }


@app.get("/api/stats")
async def get_statistics():
    """Get classification statistics"""
    try:
        stats = await db.get_statistics()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get statistics"}
        )


@app.get("/api/history")
async def get_history(limit: int = 100):
    """
    Get classification history
    
    Args:
        limit: Maximum number of records to return
    """
    try:
        history = await db.get_recent_classifications(limit=limit)
        return JSONResponse(content={"history": history})
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to get history"}
        )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    """
    await manager.connect(websocket)
    
    try:
        # Send initial statistics
        stats = await db.get_statistics()
        await websocket.send_json({
            "type": "stats",
            "data": stats
        })
        
        # Keep connection alive
        while True:
            # Wait for messages (ping/pong)
            data = await websocket.receive_text()
            
            # Send updated statistics periodically
            if data == "ping":
                stats = await db.get_statistics()
                await websocket.send_json({
                    "type": "stats",
                    "data": stats
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.post("/api/broadcast")
async def broadcast_update(update: dict):
    """
    Broadcast update to all connected WebSocket clients
    (Called internally by classifier service)
    """
    await manager.broadcast(update)
    return {"status": "broadcasted"}


# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        log_level=config.LOG_LEVEL.lower()
    )
