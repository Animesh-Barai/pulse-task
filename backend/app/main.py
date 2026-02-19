from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.database import connect_to_mongo, close_mongo_connection
from app.core.config import settings
from app.api import auth
from app.api import crdt
from app.api import tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


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

app.include_router(auth.router)
app.include_router(crdt.router)
app.include_router(tasks.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "pulsetasks-backend"}


@app.get("/")
async def root():
    return {
        "message": "Welcome to PulseTasks API",
        "version": "1.0.0",
        "docs": "/docs"
    }
