import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from state_manager import StateManager

app = FastAPI(title="Agent Orchestrator backend")
manager = StateManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)


class TaskRequest(BaseModel):
    description: str = Field(..., min_length=5)
    priority: str = Field("media")


@app.get("/state")
def get_state():
    return manager.get_state()


@app.post("/tasks")
def create_task(payload: TaskRequest):
    manager.spawn_task(payload.description, payload.priority)
    return {"status": "queued", "description": payload.description}


@app.post("/heartbeat")
def heartbeat():
    manager.heartbeat()
    return {"status": "beat"}


@app.on_event("shutdown")
def cleanup():
    manager.close()
