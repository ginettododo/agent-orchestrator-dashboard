import json
import random
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List

AGENT_NAMES = [
    "Monitor Agent",
    "Analyst Agent",
    "Executor Agent",
    "Reviewer Agent",
    "Notifier Agent",
]

DB_PATH = Path("backend/data/agents.db")
STATE_JSON = Path("site/data/agent_state.json")
TASKBUS_JSON = Path("data/task_bus.json")
METRICS_HISTORY = 10
LOG_HISTORY = 20


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dirs() -> None:
    for path in (DB_PATH.parent, STATE_JSON.parent, TASKBUS_JSON.parent):
        path.mkdir(parents=True, exist_ok=True)


class StateManager:
    def __init__(self):
        ensure_dirs()
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.init_db()

    def init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS agents (
                name TEXT PRIMARY KEY,
                status TEXT,
                progress REAL,
                last_event TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                priority TEXT,
                status TEXT,
                created_at TEXT,
                processed_at TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                message TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT,
                value REAL,
                timestamp TEXT
            )
            """
        )
        for name in AGENT_NAMES:
            cur.execute(
                "INSERT OR IGNORE INTO agents (name, status, progress, last_event) VALUES (?,?,?,?)",
                (name, "idle", 0.0, "inizializzazione"),
            )
        cur.execute("INSERT OR IGNORE INTO metrics (id, label, value, timestamp) VALUES (1, 'Efficienza media', 0.0, ?)", (now_iso(),))
        self.conn.commit()
        self.sync_files()

    def log(self, message: str) -> None:
        cur = self.conn.cursor()
        cur.execute("INSERT INTO logs (timestamp, message) VALUES (?,?)", (now_iso(), message))
        self.conn.commit()
        self._trim_logs()

    def _trim_logs(self) -> None:
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM logs ORDER BY id DESC LIMIT ?", (LOG_HISTORY,))
        ids = [row[0] for row in cur.fetchall()]
        if ids:
            min_id = min(ids)
            cur.execute("DELETE FROM logs WHERE id < ?", (min_id,))
            self.conn.commit()

    def _update_metrics(self) -> None:
        cur = self.conn.cursor()
        cur.execute("SELECT AVG(progress) as avg_progress FROM agents")
        avg = cur.fetchone()[0] or 0.0
        label = "Efficienza media"
        cur.execute(
            "INSERT INTO metrics (label, value, timestamp) VALUES (?,?,?)",
            (label, float(avg), now_iso()),
        )
        cur.execute(
            "DELETE FROM metrics WHERE id NOT IN (SELECT id FROM metrics ORDER BY id DESC LIMIT ?)" ,
            (METRICS_HISTORY,),
        )
        self.conn.commit()

    def metrics_history(self, limit: int = 10) -> List[dict]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT label, value, timestamp FROM metrics ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return [dict(row) for row in cur.fetchall()][::-1]

    def push_metric(self, label: str, value: float) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO metrics (label, value, timestamp) VALUES (?,?,?)",
            (label, float(value), now_iso()),
        )
        cur.execute(
            "DELETE FROM metrics WHERE id NOT IN (SELECT id FROM metrics ORDER BY id DESC LIMIT ?)",
            (METRICS_HISTORY,),
        )
        self.conn.commit()
        self.sync_files()

    def _random_updates(self) -> None:
        cur = self.conn.cursor()
        for name in AGENT_NAMES:
            progress = min(1.0, random.uniform(0.1, 0.8))
            cur.execute(
                "UPDATE agents SET status=?, progress=?, last_event=? WHERE name=?",
                (
                    random.choice(["idle", "working", "waiting", "sync", "review"]),
                    progress,
                    f"update automatico {random.randint(1,9)} min fa",
                    name,
                ),
            )
        self.conn.commit()

    def spawn_task(self, description: str, priority: str) -> None:
        priority = priority.lower()
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO tasks (description, priority, status, created_at) VALUES (?,?,?,?)",
            (description, priority, "pending", now_iso()),
        )
        cur.execute(
            "UPDATE agents SET status=?, progress=?, last_event=? WHERE name IN ('Monitor Agent','Analyst Agent')",
            ("working", 0.5, "nuovo task rilevato"),
        )
        self.log(f"Nuovo task '{description}' (priorità {priority}).")
        self._update_metrics()
        self.sync_files()

    def heartbeat(self) -> None:
        self._random_updates()
        self.log("Heartbeat automatico: stato sincronizzato.")
        self._update_metrics()
        self.sync_files()

    def get_state(self) -> dict:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM agents")
        agents = [dict(row) for row in cur.fetchall()]
        cur.execute("SELECT * FROM tasks ORDER BY id DESC LIMIT 20")
        tasks = [dict(row) for row in cur.fetchall()]
        cur.execute("SELECT message FROM logs ORDER BY id DESC LIMIT ?", (LOG_HISTORY,))
        logs = [row[0] for row in cur.fetchall()]
        cur.execute("SELECT label, value FROM metrics ORDER BY id DESC LIMIT 1")
        metric = cur.fetchone()
        return {
            "timestamp": now_iso(),
            "agents": agents,
            "queue": {
                "tasks": tasks,
                "pending_count": sum(1 for task in tasks if task["status"] == "pending"),
                "next_task": tasks[0]["description"] if tasks and tasks[0]["status"] == "pending" else "none",
            },
            "logs": logs,
            "metric": {"label": metric[0], "value": metric[1]} if metric else {"label": "Efficienza media", "value": 0.0},
            "metrics_history": self.metrics_history(),
        }

    def sync_files(self) -> None:
        state = self.get_state()
        STATE_JSON.write_text(json.dumps(state, indent=2))
        TASKBUS_JSON.write_text(json.dumps(state, indent=2))

    def close(self) -> None:
        self.conn.close()
