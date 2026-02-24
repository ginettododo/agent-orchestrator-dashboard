#!/usr/bin/env python3
import argparse
import subprocess
import sys
import time
from datetime import datetime


def run_heartbeat():
    result = subprocess.run([sys.executable, "site/scripts/task_bus.py", "heartbeat"], capture_output=True, text=True, check=False)
    timestamp = datetime.utcnow().isoformat()
    print(f"[{timestamp}] heartbeat → return code {result.returncode}")
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("ERROR>", result.stderr.strip())


def main():
    parser = argparse.ArgumentParser(description="Heartbeat scheduler per il task bus degli agenti")
    parser.add_argument("--interval", type=int, default=120, help="Secondi tra un battito e l'altro")
    parser.add_argument("--duration", type=int, default=900, help="Durata totale della simulazione in secondi")
    args = parser.parse_args()

    end = time.time() + args.duration
    while time.time() < end:
        run_heartbeat()
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
