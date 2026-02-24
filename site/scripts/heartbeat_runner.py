#!/usr/bin/env python3
import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from state_manager import StateManager


def main():
    parser = argparse.ArgumentParser(description="Heartbeat scheduler per il task bus degli agenti")
    parser.add_argument("--interval", type=int, default=120, help="Secondi tra un battito e l'altro")
    parser.add_argument("--duration", type=int, default=900, help="Durata totale della simulazione in secondi")
    args = parser.parse_args()

    manager = StateManager()
    end = time.time() + args.duration
    try:
        while time.time() < end:
            print("Heartbeat eseguito")
            manager.heartbeat()
            time.sleep(args.interval)
    finally:
        manager.close()


if __name__ == "__main__":
    main()
