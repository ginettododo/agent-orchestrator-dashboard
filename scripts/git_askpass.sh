#!/bin/sh
PROMPT="$1"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOKEN_FILE="$ROOT/secrets/github_token"
if [ "$PROMPT" = "Username for 'https://github.com':" ]; then
  printf 'x-access-token\n'
else
  if [ -f "$TOKEN_FILE" ]; then
    cat "$TOKEN_FILE"
  else
    printf 'x-access-token\n'
  fi
fi
