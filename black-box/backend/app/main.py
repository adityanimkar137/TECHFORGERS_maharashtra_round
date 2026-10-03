from fastapi import FastAPI

from .database import Base, engine
from . import models
from .routers import (
    runs,
    steps,
    diagnosis,
    replay,
    checkpoints,
    alternative,
    comparison,
)


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Black Box API",
    description="Backend API for AI Agent Failure Diagnosis and Replay",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Black Box Backend is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


app.include_router(runs.router)
app.include_router(steps.router)
app.include_router(diagnosis.router)
app.include_router(replay.router)
app.include_router(checkpoints.router)
app.include_router(alternative.router)
app.include_router(comparison.router)