"""Contract: our LayaHTTP client against upstream `laya-serve` (real FastAPI app, stub router, no weights).

Skipped unless `laya[serve]` is installed:  pip install "laya[serve]==0.3.20"
"""

import os
import socket
import threading
import time
import unittest
from unittest import mock

try:
    import uvicorn
    from laya.serve import create_app
except ImportError:                     # stdlib-only environments run the rest of the suite
    create_app = None

from decision_layer.client import BackendError, LayaHTTP


class StubRouter:
    """Stands in for laya.Router: same predict() signature and output shape as laya 0.3.20."""
    loaded = ["multilingual"]

    def __init__(self):
        self.calls = []

    def predict(self, state, questions, model=None):
        self.calls.append((state, model))
        answers = {}
        for qid, q in questions.items():
            if q["type"] == "noul":
                answers[qid] = {"type": "noul", "noul": 0.91, "confidence": 0.91}
            elif q["type"] == "score":
                answers[qid] = {"type": "score", "score": 1.6, "legend": {str(i): c for i, c in enumerate(q["criteria"])},
                                "probabilities": {"0": 0.1, "1": 0.2, "2": 0.7}, "confidence": 0.4}
            else:
                keys = list(q["criteria"])
                answers[qid] = {"type": "choice", "choice": keys[0],
                                "probabilities": {k: (0.8 if i == 0 else 0.2 / (len(keys) - 1)) for i, k in enumerate(keys)},
                                "confidence": 0.5}
        return {"model": model or "multilingual", "answers": answers, "usage": {"input_tokens": 42, "output_tokens": 0},
                "routing": {"model": "multilingual", "reason": "stub"}}


@unittest.skipIf(create_app is None, "laya[serve] not installed")
class LayaServeContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.router = StubRouter()
        with mock.patch.dict(os.environ, {"LAYA_API_KEY": "local-secret"}):
            app = create_app(router=cls.router)
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        cls.port = s.getsockname()[1]
        s.close()
        cls.server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=cls.port, log_level="error"))
        threading.Thread(target=cls.server.run, daemon=True).start()
        for _ in range(100):
            if cls.server.started:
                break
            time.sleep(0.05)

    @classmethod
    def tearDownClass(cls):
        cls.server.should_exit = True

    def url(self):
        return "http://127.0.0.1:%d" % self.port

    def test_predict_roundtrip_matches_panel_expectations(self):
        qs = {"stage": {"type": "choice", "instructions": "?", "criteria": {"interview": "a", "other": "b"}},
              "reply": {"type": "noul", "instructions": "?"},
              "urgency": {"type": "score", "instructions": "?", "criteria": ["low", "mid", "high"]}}
        res = LayaHTTP(self.url(), api_key="local-secret").predict({"subject": "Einladung"}, qs)
        self.assertEqual(set(res["answers"]), set(qs))
        self.assertEqual(res["answers"]["urgency"]["probabilities"], {"0": 0.1, "1": 0.2, "2": 0.7})
        self.assertEqual(self.router.calls[-1][1], None)                 # no model -> router picks by language

    def test_model_is_forwarded(self):
        LayaHTTP(self.url(), api_key="local-secret", model="multilingual").predict("x", {"q": {"type": "noul", "instructions": "?"}})
        self.assertEqual(self.router.calls[-1][1], "multilingual")

    def test_wrong_key_is_a_backend_error(self):
        with self.assertRaises(BackendError) as e:
            LayaHTTP(self.url(), api_key="wrong").predict("x", {"q": {"type": "noul", "instructions": "?"}})
        self.assertIn("401", str(e.exception))


if __name__ == "__main__":
    unittest.main()
