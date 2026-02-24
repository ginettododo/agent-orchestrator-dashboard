#!/bin/sh
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOKEN_FILE="$ROOT/secrets/vercel_token"
if [ ! -f "$TOKEN_FILE" ]; then
  echo "Missing Vercel token ($TOKEN_FILE)"
  exit 1
fi
TOKEN=$(cat "$TOKEN_FILE")
exec vercel --cwd "$ROOT/site" --prod --confirm --token "$TOKEN" --name agent-orchestrator-dashboard
