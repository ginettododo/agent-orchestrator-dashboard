#!/usr/bin/env python3
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOKEN_PATH = ROOT / "secrets" / "github_token"
if not TOKEN_PATH.exists():
    sys.exit("Missing github_token in secrets/")

GITHUB_TOKEN = TOKEN_PATH.read_text().strip()
API_BASE = "https://api.github.com"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "User-Agent": "OpenClaw-Agent",
    "Accept": "application/vnd.github+json",
    "Content-Type": "application/json",
}


def _request(method, url, payload=None):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            body = response.read().decode("utf-8")
            if not body:
                return response.getcode(), None
            return response.getcode(), json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        try:
            info = json.loads(body)
        except ValueError:
            info = {"message": body}
        return exc.code, info


def ensure_repo(owner, base_name):
    for suffix in ["", "-1", "-2", "-3"]:
        name = f"{base_name}{suffix}" if suffix else base_name
        code, _ = _request("GET", f"{API_BASE}/repos/{owner}/{name}")
        if code == 200:
            return name
        payload = {
            "name": name,
            "description": "Agent orchestrator + dashboard",
            "private": False,
        }
        code, body = _request("POST", f"{API_BASE}/user/repos", payload)
        if code == 201:
            return name
        if code in (422, 403):
            message = (body or {}).get("message", "")
            if "name already exists" in message.lower():
                continue
        raise SystemExit(f"Failed to create repo {name}: {body}")
    raise SystemExit("Could not find a free repository name")


def main():
    code, user_info = _request("GET", f"{API_BASE}/user")
    if code != 200:
        raise SystemExit(f"Failed to read user info: {user_info}")
    owner = user_info["login"]
    repo_name = ensure_repo(owner, "agent-orchestrator-dashboard")
    print(f"✅ Using repo {owner}/{repo_name}")
    print("ℹ️ Ricorda di aggiungere il secret VERCEL_TOKEN nel repository per attivare il deploy automatico.")


if __name__ == "__main__":
    main()
