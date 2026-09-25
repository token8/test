"""Evaluation harness (release checklist step 3): per-backend and panel accuracy, status shares, go/no-go."""

import json
import os
import tempfile
import unittest

from decision_layer.core import Governance, Panel
from decision_layer.infrastructure.evaluate import evaluate, go_no_go, normalise_label, render_markdown

from test_panel import POLICY, QS, Fake, Ledger, choice, noul, score

GOOD = {"stage": choice(interview=0.9, received=0.05, rejection=0.03, other=0.02), "reply": noul(0.95), "urgency": score(0.1, 0.2, 0.7)}
BAD_STAGE = dict(GOOD, stage=choice(interview=0.1, received=0.8, rejection=0.05, other=0.05))

EXAMPLES = [
    {"id": "a", "state": "x", "context": {"application": "applied"}, "labels": {"stage": "interview", "reply": True, "urgency": 2}},
    {"id": "b", "state": "y", "context": {"application": "applied"}, "labels": {"stage": "interview", "reply": True, "urgency": 1}},
]


class EvaluateTest(unittest.TestCase):
    def test_labels_normalise_to_answer_labels(self):
        self.assertEqual(normalise_label(True), "true")
        self.assertEqual(normalise_label(2), "2")
        self.assertEqual(normalise_label("interview"), "interview")

    def test_per_backend_and_panel_accuracy(self):
        panel = Panel([Fake("laya", BAD_STAGE), Fake("jev", GOOD, remote=True, usage=100)], Governance(POLICY), Ledger())
        rep = evaluate(panel, QS, EXAMPLES)
        st = rep["questions"]["stage"]
        self.assertEqual((st["n"], st["accuracy"]["laya"], st["accuracy"]["jev"]), (2, 0.0, 1.0))
        self.assertEqual(st["status"]["review"], 1.0)              # disagreement -> review, every time
        self.assertIsNone(st["act_accuracy"])                      # nothing acted on
        self.assertEqual(rep["questions"]["urgency"]["accuracy"]["panel"], 0.5)
        self.assertEqual(rep["remote_input_tokens"], 200)

    def test_unlabelled_questions_are_skipped(self):
        panel = Panel([Fake("laya", GOOD)], Governance(POLICY), Ledger())
        rep = evaluate(panel, QS, [{"id": "c", "state": "z", "labels": {"reply": True}}])
        self.assertEqual(rep["questions"]["stage"]["n"], 0)
        self.assertEqual(rep["questions"]["reply"]["n"], 1)

    def test_go_no_go_and_report(self):
        panel = Panel([Fake("laya", GOOD), Fake("jev", GOOD, remote=True)], Governance(POLICY), Ledger())
        rep = evaluate(panel, QS, EXAMPLES)
        verdict = go_no_go(rep, min_act_accuracy=0.97, max_review_share=0.25)
        self.assertTrue(verdict["reply"]["go"])
        self.assertFalse(verdict["urgency"]["go"])                 # acted on a wrong label once
        md = render_markdown(rep, verdict)
        self.assertIn("| stage |", md)
        self.assertIn("NO-GO", md)
        self.assertNotIn("\"x\"", md)                              # no message text in the report


if __name__ == "__main__":
    unittest.main()
