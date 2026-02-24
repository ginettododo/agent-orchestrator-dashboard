#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "task_bus.json"

def load_state():
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text())
        except json.JSONDecodeError:
            pass
    
    # Default state if file doesn't exist or is corrupted
    state = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agents": [
            {"name": name, "status": "idle", "progress": 0.0, "last_event": "reset"}
            for name in ["Monitor Agent", "Analyst Agent", "Executor Agent", "Reviewer Agent", "Notifier Agent"]
        ],
        "queue": {"tasks": [], "pending_count": 0, "last_processed_at": None},
        "logs": ["Task Bus resettato."]
    }
    save_state(state)
    return state

def save_state(state):
    state["timestamp"] = datetime.now(timezone.utc).isoformat()
    state["queue"]["pending_count"] = len([t for t in state["queue"]["tasks"] if t["status"] == "pending"])
    # Keep only last 50 logs
    state["logs"] = state["logs"][:50]
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2))

def spawn_task(description, priority="media"):
    state = load_state()
    task = {
        "id": f"task_{int(datetime.now().timestamp())}",
        "description": description,
        "priority": priority,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "assigned_to": None,
        "history": []
    }
    state["queue"]["tasks"].append(task)
    state["logs"].insert(0, f"NUOVO TASK: {description} (Priorità: {priority})")
    save_state(state)
    return task["id"]

def claim_task(agent_name):
    state = load_state()
    # Find first pending task
    task = next((t for t in state["queue"]["tasks"] if t["status"] == "pending"), None)
    if not task:
        return None
    
    task["status"] = "in_progress"
    task["assigned_to"] = agent_name
    task["history"].append({"at": datetime.now(timezone.utc).isoformat(), "event": f"Preso in carico da {agent_name}"})
    
    # Update agent status
    for a in state["agents"]:
        if a["name"] == agent_name:
            a["status"] = "working"
            a["last_event"] = f"Iniziato task {task['id']}"
            
    state["logs"].insert(0, f"TASK {task['id']} assegnato a {agent_name}")
    save_state(state)
    return task

def complete_task(task_id, result="Completato"):
    state = load_state()
    task = next((t for t in state["queue"]["tasks"] if t["id"] == task_id), None)
    if not task:
        return False
    
    task["status"] = "completed"
    task["history"].append({"at": datetime.now(timezone.utc).isoformat(), "event": f"Completato: {result}"})
    
    # Update agent status
    agent_name = task["assigned_to"]
    for a in state["agents"]:
        if a["name"] == agent_name:
            a["status"] = "idle"
            a["progress"] = 1.0
            a["last_event"] = f"Completato task {task_id}"
            
    state["logs"].insert(0, f"TASK {task_id} completato da {agent_name}")
    save_state(state)
    return True

def main():
    parser = argparse.ArgumentParser(description="Task bus per la dashboard degli agenti")
    subparsers = parser.add_subparsers(dest="command", help="azioni")
    
    subparsers.add_parser("status", help="Mostra lo stato attuale")
    
    spawn = subparsers.add_parser("spawn", help="Inserisce un nuovo task")
    spawn.add_argument("description", help="Descrizione del task")
    spawn.add_argument("--priority", choices=["bassa", "media", "alta"], default="media")
    
    claim = subparsers.add_parser("claim", help="Un agente prende in carico un task")
    claim.add_argument("agent", help="Nome dell'agente")
    
    complete = subparsers.add_parser("complete", help="Segna un task come completato")
    complete.add_argument("id", help="ID del task")
    complete.add_argument("--result", default="Completato")

    args = parser.parse_args()

    if args.command == "status":
        state = load_state()
        print(json.dumps(state, indent=2))
    elif args.command == "spawn":
        tid = spawn_task(args.description, args.priority)
        print(tid) # Solo ID per scripting
    elif args.command == "claim":
        task = claim_task(args.agent)
        if task:
            print(task['id'])
        else:
            print("NONE")
    elif args.command == "complete":
        if complete_task(args.id, args.result):
            print("OK")
        else:
            print("ERROR")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
