#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from state_manager import StateManager


def describe_queue(queue):
    tasks = queue.get("tasks", [])
    pending = queue.get("pending_count", 0)
    next_task = queue.get("next_task", "nessuno")
    return f"{pending} task in coda · prossimo: {next_task}"


def print_state(state):
    print("Stato attuale")
    print(f"  Timestamp (UTC): {state['timestamp']}")
    print("  Agenti:")
    for agent in state["agents"]:
        progress = int(agent.get("progress", 0) * 100)
        print(f"    • {agent['name']}: {agent['status']} · {progress}% · {agent['last_event']}")
    print(f"  Coda: {describe_queue(state['queue'])}")
    print("  Metriche:")
    print(f"    • {state['metric']['label']}: {state['metric']['value'] * 100:.1f}%")
    print("  Log recenti:")
    for log in state["logs"][:5]:
        print(f"    - {log}")


def main():
    parser = argparse.ArgumentParser(description="Task bus CLI aggiornato")
    parser.add_argument("command", choices=["status", "spawn", "heartbeat"], help="Azione da eseguire")
    parser.add_argument("--task", help="Descrizione del task da aggiungere")
    parser.add_argument("--priority", choices=["bassa", "media", "alta"], default="media")
    args = parser.parse_args()

    manager = StateManager()

    if args.command == "status":
        print_state(manager.get_state())
    elif args.command == "spawn":
        if not args.task:
            parser.error("--task è obbligatorio per spawn")
        manager.spawn_task(args.task, args.priority)
        print_state(manager.get_state())
    elif args.command == "heartbeat":
        manager.heartbeat()
        print_state(manager.get_state())

    manager.close()


if __name__ == "__main__":
    main()
