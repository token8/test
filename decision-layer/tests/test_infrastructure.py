"""Infrastructure: .env loading, ledger, end-to-end over HTTP, and the job-crm config files."""

import json
import os
import shutil
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock

from decision_layer.infrastructure import JsonlLedger, load_env, load_governance, load_questions, open_panel

JOB_CRM = os.path.join(os.path.dirname(__file__), "..", "..", "job-crm")


def read(*path):
    with open(os.path.join(*path)) as f:
        return f.read()


class EnvTest(unittest.TestCase):
    def test_parse_and_precedence(self):
        with tempfile.TemporaryDirectory() as d, mock.patch.dict(os.environ, {"KEEP": "real"}, clear=False):
            path = os.path.join(d, ".env")
            with open(path, "w") as f:
                f.write('# c\nexport A="x y"\nB=\'q\'\nC=plain # note\nKEEP=file\nbroken line\n')
            load_env(path)
            self.assertEqual((os.environ["A"], os.environ["B"], os.environ["C"], os.environ["KEEP"]),
                             ("x y", "q", "plain", "real"))

    def test_missing_file_is_fine(self):
        self.assertEqual(load_env("/nonexistent/.env"), {})


class LedgerTest(unittest.TestCase):
    def test_spend_counts_this_month_only(self):
        with tempfile.TemporaryDirectory() as d:
            led = JsonlLedger(d)
            led.record_call({"ts": "1999-01-01T00:00:00+00:00", "cost_usd": 9.0})
            from datetime import datetime, timezone
            led.record_call({"ts": datetime.now(timezone.utc).isoformat(), "cost_usd": 0.25})
            self.assertAlmostEqual(led.spend_this_month(), 0.25)


class FakeModels(BaseHTTPRequestHandler):
    """Laya sidecar at /predict and Jev at /v1/systemone on one port."""
    jev_status = 200

    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path == "/v1/systemone" and self.jev_status != 200:
            self.send_response(self.jev_status)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        answers = {}
        for qid, q in body["questions"].items():
            if q["type"] == "noul":
                answers[qid] = {"type": "noul", "noul": 0.97}
            elif q["type"] == "score":
                answers[qid] = {"type": "score", "probabilities": {"0": 0.05, "1": 0.15, "2": 0.8}}
            else:
                answers[qid] = {"type": "choice", "probabilities": {k: (0.9 if k == "interview" else 0.1 / (len(q["criteria"]) - 1))
                                                                     for k in q["criteria"]}}
        out = {"answers": answers}
        if self.path == "/v1/systemone":
            assert self.headers["Authorization"] == "Bearer test-key"
            out |= {"model": body["model"], "usage": {"input_tokens": 400}}
        data = json.dumps(out).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class EndToEndTest(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeModels)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = "http://127.0.0.1:%d" % self.server.server_port
        self.product = tempfile.mkdtemp()
        shutil.copytree(os.path.join(JOB_CRM, "decisions"), os.path.join(self.product, "decisions"))
        with open(os.path.join(self.product, ".env"), "w") as f:
            f.write("TYPESAFE_API_KEY=test-key\nLAYA_URL=%s\nJEV_MODEL=jev-test\n" % self.url)
        self.env = mock.patch.dict(os.environ, {}, clear=False)
        self.env.start()
        for k in ("TYPESAFE_API_KEY", "LAYA_URL", "JEV_MODEL", "DECISION_REMOTE", "DECISION_LOG_DIR"):
            os.environ.pop(k, None)

    def tearDown(self):
        self.env.stop()
        self.server.shutdown()
        self.server.server_close()
        shutil.rmtree(self.product)
        FakeModels.jev_status = 200

    def _panel(self):
        p = open_panel(self.product)
        p.backends[1].url = self.url + "/v1/systemone"          # point Jev at the fake
        p.backends[1].retries = 0
        return p

    def test_parallel_decision_is_logged(self):
        d = self._panel().decide({"subject": "Interview", "body": "private"}, load_questions(self.product),
                                 {"application": "applied"})
        self.assertEqual(d.status("stage"), "act")
        self.assertEqual(d.results["stage"]["sources"], ["jev", "laya"])
        self.assertEqual(d.results["stage"]["transition"], {"from": "applied", "to": "interviewing"})
        logs = os.path.join(self.product, "logs")
        call = json.loads(read(logs, "llm_calls.jsonl").splitlines()[0])
        self.assertEqual((call["model"], call["input_tokens"]), ("jev-test", 400))
        self.assertNotIn("private", read(logs, "decisions.jsonl"))

    def test_jev_http_failure_degrades(self):
        FakeModels.jev_status = 503
        d = self._panel().decide("Interview on Monday?", load_questions(self.product), {"application": "applied"})
        self.assertEqual(d.results["stage"]["sources"], ["laya"])
        self.assertEqual(d.status("stage"), "review")          # 0.9 < degraded 0.95
        self.assertFalse(d.record["backends"]["jev"]["ok"])

    def test_kill_switch_from_env_file(self):
        with open(os.path.join(self.product, ".env"), "a") as f:
            f.write("DECISION_REMOTE=0\n")
        d = self._panel().decide("x", load_questions(self.product), {"application": "applied"})
        self.assertNotIn("jev", d.record["backends"])
        self.assertIn("kill_switch", d.record["remote_blocked"])


class JobCrmConfigTest(unittest.TestCase):
    """The shipped job-crm governance and questions stay consistent with each other."""

    def test_config_is_consistent(self):
        gov, qs = load_governance(JOB_CRM), load_questions(JOB_CRM)
        self.assertLessEqual(set(gov.policy["questions"]), set(qs))
        fsm = gov.fsm["application"]
        self.assertEqual(set(fsm["map"]), set(qs["stage"]["criteria"]))
        states = set(fsm["transitions"]) | {s for t in fsm["transitions"].values() for s in t}
        self.assertLessEqual({s for s in fsm["map"].values() if s}, states)
        self.assertLessEqual(set(fsm["approval_required"]), states)
        self.assertEqual(gov.inherits["version"], "3.1")

    def test_secrets_are_ignored(self):
        ignore = read(JOB_CRM, ".gitignore").split()
        self.assertIn(".env", ignore)
        self.assertIn("logs/", ignore)


if __name__ == "__main__":
    unittest.main()
