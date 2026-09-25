"""Infrastructure for the decision panel: .env loading, JSONL ledger, and wiring a product folder.

    from decision_layer.infrastructure import open_panel, load_questions
    panel = open_panel("example")                     # reads example/.env and example/decisions/*
    d = panel.decide(state, load_questions("example"), {"application": "applied"})
"""

import json
import os
import threading
from datetime import datetime, timezone

from ..client import JEV_URL, Jev, LayaHTTP, LAYA_URL
from ..core import Governance, Panel


def load_env(path, override=False):
    """Minimal .env reader: KEY=VALUE lines, optional `export`, quotes and # comments.
    Real environment variables win unless override=True. A missing file is not an error."""
    if not os.path.exists(path):
        return {}
    loaded = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.removeprefix("export ").split("=", 1)
            key, value = key.strip(), value.strip()
            if value[:1] in "\"'" and value[-1:] == value[:1] and len(value) > 1:
                value = value[1:-1]
            elif " #" in value:
                value = value.split(" #", 1)[0].rstrip()
            if override or key not in os.environ:
                os.environ[key] = value
                loaded[key] = value
    return loaded


class JsonlLedger:
    """Append-only audit trail: decisions.jsonl (no text) and llm_calls.jsonl (tokens, cost; §5)."""

    def __init__(self, directory):
        self.dir, self.lock = directory, threading.Lock()
        os.makedirs(directory, exist_ok=True)

    def _append(self, name, rec):
        with self.lock, open(os.path.join(self.dir, name), "a") as f:
            f.write(json.dumps(rec, sort_keys=True) + "\n")

    def record_call(self, rec):
        self._append("llm_calls.jsonl", rec)

    def record_decision(self, rec):
        self._append("decisions.jsonl", rec)

    def spend_this_month(self):
        path, month = os.path.join(self.dir, "llm_calls.jsonl"), datetime.now(timezone.utc).strftime("%Y-%m")
        if not os.path.exists(path):
            return 0.0
        with self.lock, open(path) as f:
            return sum(r.get("cost_usd", 0.0) for r in map(json.loads, filter(str.strip, f))
                       if r.get("ts", "").startswith(month))


def load_governance(product_dir):
    with open(os.path.join(product_dir, "decisions", "governance.json")) as f:
        return Governance(json.load(f))


def load_questions(product_dir):
    with open(os.path.join(product_dir, "decisions", "questions.json")) as f:
        return {k: v for k, v in json.load(f).items() if not k.startswith("$")}


def open_panel(product_dir, env_file=".env"):
    """Build a panel from a product folder: its .env (secrets), governance.json and log dir."""
    load_env(os.path.join(product_dir, env_file))
    backends = [LayaHTTP(os.environ.get("LAYA_URL", LAYA_URL), model=os.environ.get("LAYA_MODEL") or None,
                         api_key=os.environ.get("LAYA_API_KEY") or None)]
    if os.environ.get("TYPESAFE_API_KEY"):
        backends.append(Jev(os.environ["TYPESAFE_API_KEY"], model=os.environ.get("JEV_MODEL", "jev-latest"),
                            url=os.environ.get("JEV_URL", JEV_URL)))
    ledger = JsonlLedger(os.path.join(product_dir, os.environ.get("DECISION_LOG_DIR", "logs")))
    return Panel(backends, load_governance(product_dir), ledger,
                 remote_enabled=os.environ.get("DECISION_REMOTE", "1") != "0")
