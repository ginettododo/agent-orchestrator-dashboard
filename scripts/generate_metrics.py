#!/usr/bin/env python3
import argparse
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from state_manager import StateManager


def main():
    parser = argparse.ArgumentParser(description="Genera metriche storiche per l'agent bus")
    parser.add_argument("--iterations", type=int, default=12, help="Quanti punti creare")
    parser.add_argument("--interval", type=int, default=2, help="Secondi tra un punto e l'altro (simulati)")
    parser.add_argument("--label", default="Efficienza media", help="Label dei punti")
    args = parser.parse_args()

    manager = StateManager()
    try:
        for i in range(args.iterations):
            value = max(0.05, min(1.0, random.random() * 0.6 + 0.3))
            manager.push_metric(args.label, value)
            print(f"[{i+1}/{args.iterations}] metric pushed: {value:.2f}")
            time.sleep(args.interval)
    finally:
        manager.close()

    print("Metriche generate.")


if __name__ == "__main__":
    main()
