import unittest

from decision_layer import BackendError, DecisionClient, Policy, top_probability
from decision_layer.presets import JOB_EMAIL_POLICIES, job_email_questions


def choice(p):
    return {"type": "choice", "choice": max(p, key=p.get), "probabilities": p}


class Fake:
    def __init__(self, name, answers=None, fail=False):
        self.name, self.answers, self.fail, self.calls = name, answers or {}, fail, []

    def predict(self, state, questions):
        self.calls.append(set(questions))
        if self.fail:
            raise BackendError(self.name + " down")
        return {"answers": {q: self.answers[q] for q in questions if q in self.answers}}


QS = {
    "stage": {"type": "choice", "criteria": ["a", "b"]},
    "reply": {"type": "noul"},
    "urgency": {"type": "score", "criteria": ["low", "high"]},
}
REMOTE = {
    "stage": choice({"a": 0.99, "b": 0.01}),
    "reply": {"type": "noul", "noul": 0.02},
    "urgency": {"type": "score", "score": 1.0, "probabilities": {"0": 0.1, "1": 0.9}},
}


class DecisionClientTest(unittest.TestCase):
    def test_confident_laya_answers_stay_local(self):
        laya = Fake("laya", {"stage": choice({"a": 0.95, "b": 0.05}), "reply": {"type": "noul", "noul": 0.03},
                             "urgency": REMOTE["urgency"]})
        jev = Fake("jev", REMOTE)
        res = DecisionClient(laya, jev).decide("s", QS)
        self.assertEqual(res.sources, {"stage": "laya", "reply": "laya", "urgency": "jev"})
        self.assertEqual(jev.calls, [{"urgency"}])        # score type always escalates

    def test_low_confidence_escalates(self):
        laya = Fake("laya", {"stage": choice({"a": 0.6, "b": 0.4}), "reply": {"type": "noul", "noul": 0.5},
                             "urgency": REMOTE["urgency"]})
        res = DecisionClient(laya, Fake("jev", REMOTE), always_remote=()).decide("s", QS)
        self.assertEqual(res.sources, {"stage": "jev", "reply": "jev", "urgency": "laya"})
        self.assertEqual(res.escalated, ["stage", "reply"])

    def test_laya_down_everything_goes_to_jev(self):
        res = DecisionClient(Fake("laya", fail=True), Fake("jev", REMOTE)).decide("s", QS)
        self.assertEqual(set(res.sources.values()), {"jev"})

    def test_private_question_never_leaves_the_machine(self):
        laya = Fake("laya", {"stage": choice({"a": 0.6, "b": 0.4})})
        jev = Fake("jev", REMOTE)
        res = DecisionClient(laya, jev).decide("s", {"stage": QS["stage"]}, {"stage": Policy(allow_remote=False)})
        self.assertEqual(jev.calls, [])
        self.assertEqual(res.sources["stage"], "laya")
        self.assertEqual(res.fallback_failed, ["stage"])  # kept, but flagged as weak

    def test_jev_down_keeps_weak_laya_answer(self):
        laya = Fake("laya", {"stage": choice({"a": 0.6, "b": 0.4})})
        res = DecisionClient(laya, Fake("jev", fail=True)).decide("s", {"stage": QS["stage"]})
        self.assertEqual((res.sources["stage"], res.fallback_failed), ("laya", ["stage"]))

    def test_both_down_raises(self):
        with self.assertRaises(BackendError):
            DecisionClient(Fake("laya", fail=True), Fake("jev", fail=True)).decide("s", QS)

    def test_no_fallback_configured(self):
        laya = Fake("laya", {"stage": choice({"a": 0.6, "b": 0.4})})
        res = DecisionClient(laya, None).decide("s", {"stage": QS["stage"]})
        self.assertEqual(res.fallback_failed, ["stage"])

    def test_top_probability(self):
        self.assertAlmostEqual(top_probability({"type": "noul", "noul": 0.1}), 0.9)
        self.assertAlmostEqual(top_probability(choice({"a": 0.3, "b": 0.7})), 0.7)

    def test_presets_have_policies_for_their_questions(self):
        self.assertLessEqual(set(JOB_EMAIL_POLICIES), set(job_email_questions()))


if __name__ == "__main__":
    unittest.main()
