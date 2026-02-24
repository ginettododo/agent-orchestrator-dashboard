#!/usr/bin/env python3
import argparse
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from state_manager import StateManager

MESSAGES = [
    "Analizza i log di sistema e genera un report compatto",
    "Prepara un briefing sul nuovo stack di agenti e invialo al canale",
    "Aggiorna la dashboard con le ultime metriche di qualità",
    "Genera le istruzioni per il prossimo rollout h24",
    "Raccogli le richieste in attesa e classificale per priorità",
]


def main():
    parser = argparse.ArgumentParser(description="Simula task automatici per la dashboard degli agenti")
    parser.add_argument("--iterations", type=int, default=5, help="Quanti task generare")
    parser.add_argument("--interval", type=float, default=30, help="Secondi tra un task e l'altro")
    parser.add_argument("--priority", choices=["bassa", "media", "alta"], default="media")
    args = parser.parse_args()

    manager = StateManager()
    try:
        for idx in range(args.iterations):
            task = random.choice(MESSAGES)
            print(f"[{idx+1}/{args.iterations}] spawn task: {task} (priorità {args.priority})")
            manager.spawn_task(task, args.priority)
            time.sleep(args.interval)
    finally:
        manager.close()

    print("Simulazione completata.")


if __name__ == "__main__":
    main()
