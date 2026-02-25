from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from socketio import ASGIApp, AsyncServer
from app.db.database import connect_to_mongo, close_mongo_connection, get_redis
from app.core.config import settings
from app.api import auth
from app.api import crdt
from app.api import tasks
from app.api import socket_events
from app.api import presence


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    # Initialize Redis connection
    get_redis()
    yield
    await close_mongo_connection()


# Create Socket.IO server
sio = AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# Create ASGI app for Socket.IO
socket_app = ASGIApp(sio)

# Register all Socket.IO event handlers
socket_events.register_socket_events(sio)

app = FastAPI(
    title="PulseTasks API",
    description="Real-time collaborative task management platform with AI-powered features",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include FastAPI routers
app.include_router(auth.router)
app.include_router(crdt.router)
app.include_router(tasks.router)
app.include_router(presence.router)

# Mount Socket.IO on FastAPI (before other routes)
app.mount("/socket.io", socket_app)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "pulsetasks-backend",
        "socketio": "running"
    }

@app.get("/health/socket")
async def socket_health():
    return {
        "status": "healthy",
        "server": "socketio",
        "async_mode": "asgi"
    }

@app.get("/")
async def root():
    return {
        "message": "Welcome to PulseTasks API",
        "version": "1.0.0",
        "docs": "/docs"
    }
