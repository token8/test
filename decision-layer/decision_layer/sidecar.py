"""Laya as a loopback HTTP sidecar, so non-Python apps (and DecisionClient) can call it.

    pip install laya
    python -m decision_layer.sidecar            # 127.0.0.1:8771

    POST /predict  {"state": ..., "questions": {...}}  -> Laya's predict() result
    GET  /health   -> {"ok": true, "checkpoint": ...}

LAYA_CHECKPOINT picks a subfolder ("", "multilingual", "typed-decisions"); LAYA_PORT the port.
One model, one lock: a GPU serves one forward pass at a time.
"""

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import laya

CHECKPOINT = os.environ.get("LAYA_CHECKPOINT", "")
PORT = int(os.environ.get("LAYA_PORT", "8771"))

agent = laya.load("convaiinnovations/laya", **({"subfolder": CHECKPOINT} if CHECKPOINT else {}))
lock = threading.Lock()

# Warm-up: the first call at a new shape compiles kernels and is several times slower.
agent.predict("Warm-up.", {"w": {"type": "noul", "instructions": "Is this a warm-up message?"}})


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"          # keep-alive

    def _send(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"ok": True, "checkpoint": CHECKPOINT or "english"})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/predict":
            return self._send(404, {"error": "not found"})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            with lock:
                self._send(200, agent.predict(body["state"], body["questions"]))
        except (ValueError, KeyError, TypeError) as e:
            self._send(400, {"error": str(e)})

    def log_message(self, *args):
        pass                                # request text may be personal data; do not log it


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
