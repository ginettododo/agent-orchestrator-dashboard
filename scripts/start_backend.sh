#!/bin/sh
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec uvicorn backend.app:app --host 0.0.0.0 --port 8001 --reload --log-level info
