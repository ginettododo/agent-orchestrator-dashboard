#!/usr/bin/env python3
import argparse
import random
import subprocess
import sys
import time

MESSAGES = [
    "Analizza i log di sistema e genera un report compatto",
    "Prepara un briefing sul nuovo stack di agenti e invialo al canale",
    "Aggiorna la dashboard con le ultime metriche di qualità",
    "Genera le istruzioni per il prossimo rollout h24",
    "Raccogli le richieste in attesa e classificale per priorità",
]


def run_command(args):
    try:
        subprocess.run(args, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"Errore: {exc}")
        sys.exit(exc.returncode)


def main():
    parser = argparse.ArgumentParser(description="Simula task automatici per la dashboard degli agenti")
    parser.add_argument("--iterations", type=int, default=5, help="Quanti task generare")
    parser.add_argument("--interval", type=float, default=30, help="Secondi tra un task e l'altro")
    parser.add_argument("--priority", choices=["bassa", "media", "alta"], default="media")
    args = parser.parse_args()

    for idx in range(args.iterations):
        task = random.choice(MESSAGES)
        print(f"[{idx+1}/{args.iterations}] Spawn task: {task} (priorità {args.priority})")
        run_command([
            sys.executable,
            "site/scripts/task_bus.py",
            "spawn",
            "--task",
            task,
            "--priority",
            args.priority,
        ])
        if idx < args.iterations - 1:
            time.sleep(args.interval)

    print("Simulazione completata.")


if __name__ == "__main__":
    main()
