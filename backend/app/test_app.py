# Minimal FastAPI test app
# Only includes routers that have working imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api import auth
from app.api import tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # No database connection needed for integration tests with mocked services
    yield


app = FastAPI(
    title="PulseTasks API - Test",
    description="Minimal test app for task API integration tests",
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

# Only include routers that work without dependencies
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "pulsetasks-backend-test"}
