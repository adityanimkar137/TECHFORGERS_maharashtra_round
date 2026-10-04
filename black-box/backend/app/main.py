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
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
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
