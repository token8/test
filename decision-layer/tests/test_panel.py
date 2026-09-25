"""Contract tests for SPEC.md: combining votes, governance rules, parallel panel, failure paths."""

import threading
import time
import unittest

from decision_layer.core import Governance, GovernanceError, Panel, combine

QS = {
    "stage": {"type": "choice", "instructions": "?", "criteria": {"received": "", "interview": "", "rejection": "", "other": ""}},
    "reply": {"type": "noul", "instructions": "?"},
    "urgency": {"type": "score", "instructions": "?", "criteria": ["low", "mid", "high"]},
}

POLICY = {
    "version": "test-1",
    "inherits": {"document": "CoreState OSS: Active Constitution", "version": "3.1"},
    "remote_authorization": {"granted_by": "owner", "date": "2026-09-25", "scope": "tests"},
    "budget": {"monthly_usd_ceiling": 5.0, "price_per_mtok": {"jev": 0.042}},
    "weights": {"default": {"laya": 1.0, "jev": 1.0}, "score": {"laya": 0.5, "jev": 1.5}},
    "defaults": {"act_threshold": 0.8, "degraded_threshold": 0.95, "require_agreement": True,
                 "autonomy": "act", "remote": True},
    "questions": {
        "stage": {"fsm": "application"},
        "reply": {},
        "urgency": {"require_agreement": False, "act_threshold": 0.6},
    },
    "fsm": {"application": {
        "map": {"received": "applied", "interview": "interviewing", "rejection": "rejected", "other": None},
        "transitions": {"(none)": ["applied"], "applied": ["interviewing", "rejected"],
                        "interviewing": ["interviewing", "rejected"]},
        "approval_required": ["rejected"],
    }},
}


def choice(**p):
    return {"type": "choice", "choice": max(p, key=p.get), "probabilities": p}


def noul(p):
    return {"type": "noul", "noul": p}


def score(*p):
    return {"type": "score", "probabilities": {str(i): v for i, v in enumerate(p)}}


class Fake:
    def __init__(self, name, answers=None, remote=False, fail=False, delay=0.0, usage=None):
        self.name, self.remote, self.answers, self.fail, self.delay = name, remote, answers or {}, fail, delay
        self.usage, self.calls = usage, []

    def predict(self, state, questions):
        self.calls.append(set(questions))
        time.sleep(self.delay)
        if self.fail:
            raise RuntimeError(self.name + " down")
        out = {"answers": {q: self.answers[q] for q in questions if q in self.answers}, "model": self.name + "-1"}
        if self.usage:
            out["usage"] = {"input_tokens": self.usage}
        return out


class Ledger:
    def __init__(self, spend=0.0):
        self.spend, self.calls, self.decisions = spend, [], []

    def spend_this_month(self):
        return self.spend

    def record_call(self, rec):
        self.calls.append(rec)

    def record_decision(self, rec):
        self.decisions.append(rec)


AGREE = {"stage": choice(interview=0.9, received=0.05, rejection=0.03, other=0.02),
         "reply": noul(0.95), "urgency": score(0.1, 0.2, 0.7)}


def panel(laya=None, jev=None, policy=POLICY, **kw):
    backends = [b for b in (laya, jev) if b is not None]
    return Panel(backends, Governance(policy), kw.pop("ledger", Ledger()), **kw)


# ---------------------------------------------------------------- combine (§5 of the spec)
class CombineTest(unittest.TestCase):
    def test_noul_weighted_mean(self):
        c = combine({"laya": noul(0.9), "jev": noul(0.7)}, {"laya": 1, "jev": 1})
        self.assertEqual(c["value"], "true")
        self.assertAlmostEqual(c["probability"], 0.8)
        self.assertTrue(c["agree"])

    def test_choice_weights_and_disagreement(self):
        c = combine({"laya": choice(a=0.6, b=0.4), "jev": choice(a=0.1, b=0.9)}, {"laya": 0.5, "jev": 1.5})
        self.assertEqual(c["value"], "b")
        self.assertAlmostEqual(c["probability"], (0.5 * 0.4 + 1.5 * 0.9) / 2)
        self.assertFalse(c["agree"])

    def test_missing_option_counts_as_zero(self):
        c = combine({"laya": choice(a=1.0), "jev": choice(b=1.0)}, {})
        self.assertAlmostEqual(sum(c["probabilities"].values()), 1.0)

    def test_single_vote_trivially_agrees(self):
        self.assertTrue(combine({"laya": noul(0.1)}, {})["agree"])


# ---------------------------------------------------------------- governance file (failure path 8)
class GovernanceLoadTest(unittest.TestCase):
    def test_missing_required_keys_fail_loudly(self):
        with self.assertRaises(GovernanceError):
            Governance({"version": "x"})

    def test_unknown_fsm_reference_fails(self):
        bad = dict(POLICY, questions={"stage": {"fsm": "nope"}})
        with self.assertRaises(GovernanceError):
            Governance(bad)

    def test_bad_autonomy_fails(self):
        bad = dict(POLICY, defaults=dict(POLICY["defaults"], autonomy="yolo"))
        with self.assertRaises(GovernanceError):
            Governance(bad)


# ---------------------------------------------------------------- panel and rules
class PanelTest(unittest.TestCase):
    def test_backends_run_in_parallel(self):
        laya, jev = Fake("laya", AGREE, delay=0.2), Fake("jev", AGREE, remote=True, delay=0.2)
        t0 = time.perf_counter()
        panel(laya, jev).decide("s", QS, {"application": "applied"})
        self.assertLess(time.perf_counter() - t0, 0.35)

    def test_agreement_acts(self):
        d = panel(Fake("laya", AGREE), Fake("jev", AGREE, remote=True)).decide("s", QS, {"application": "applied"})
        self.assertEqual(d.status("stage"), "act")
        self.assertEqual(d.results["stage"]["transition"], {"from": "applied", "to": "interviewing"})
        self.assertEqual(d.status("reply"), "act")
        self.assertEqual(sorted(d.results["stage"]["sources"]), ["jev", "laya"])

    def test_disagreement_goes_to_review(self):
        other = dict(AGREE, reply=noul(0.1))
        d = panel(Fake("laya", AGREE), Fake("jev", other, remote=True)).decide("s", QS, {"application": "applied"})
        self.assertEqual(d.status("reply"), "review")
        self.assertIn("gap", d.rules("reply"))

    def test_low_confidence_goes_to_review(self):
        weak = dict(AGREE, reply=noul(0.7))
        d = panel(Fake("laya", weak), Fake("jev", weak, remote=True)).decide("s", QS, {"application": "applied"})
        self.assertEqual(d.status("reply"), "review")

    def test_score_uses_type_weights_without_agreement(self):
        a = dict(AGREE, urgency=score(0.6, 0.3, 0.1))          # Laya says low, Jev says high
        d = panel(Fake("laya", a), Fake("jev", AGREE, remote=True)).decide("s", QS, {"application": "applied"})
        self.assertEqual(d.results["urgency"]["value"], "2")    # Jev weighted 1.5 vs 0.5
        self.assertEqual(d.status("urgency"), "review")         # 0.55 < 0.6 threshold

    # -- state and heartbeat
    def test_terminal_transition_is_proposed(self):
        r = dict(AGREE, stage=choice(rejection=0.95, received=0.02, interview=0.02, other=0.01))
        d = panel(Fake("laya", r), Fake("jev", r, remote=True)).decide("s", QS, {"application": "applied"})
        self.assertEqual(d.status("stage"), "propose")
        self.assertIn("heartbeat", d.rules("stage"))

    def test_illegal_transition_goes_to_review(self):
        r = dict(AGREE, stage=choice(received=0.95, interview=0.02, rejection=0.02, other=0.01))
        d = panel(Fake("laya", r), Fake("jev", r, remote=True)).decide("s", QS, {"application": "interviewing"})
        self.assertEqual(d.status("stage"), "review")
        self.assertIn("state", d.rules("stage"))

    def test_same_state_is_no_transition(self):
        d = panel(Fake("laya", AGREE), Fake("jev", AGREE, remote=True)).decide("s", QS, {"application": "interviewing"})
        self.assertEqual((d.status("stage"), d.results["stage"]["transition"]), ("act", None))

    def test_label_without_state_mapping(self):
        r = dict(AGREE, stage=choice(other=0.95, received=0.02, interview=0.02, rejection=0.01))
        d = panel(Fake("laya", r), Fake("jev", r, remote=True)).decide("s", QS, {"application": "applied"})
        self.assertEqual((d.status("stage"), d.results["stage"]["transition"]), ("act", None))

    def test_missing_context_means_new_record(self):
        r = dict(AGREE, stage=choice(received=0.95, interview=0.02, rejection=0.02, other=0.01))
        d = panel(Fake("laya", r), Fake("jev", r, remote=True)).decide("s", QS)
        self.assertEqual(d.results["stage"]["transition"], {"from": "(none)", "to": "applied"})

    def test_autonomy_propose(self):
        pol = dict(POLICY, questions=dict(POLICY["questions"], reply={"autonomy": "propose"}))
        d = panel(Fake("laya", AGREE), Fake("jev", AGREE, remote=True), policy=pol).decide("s", QS, {"application": "applied"})
        self.assertEqual(d.status("reply"), "propose")

    # -- failure paths (spec §6)
    def test_fp1_local_down(self):
        d = panel(Fake("laya", fail=True), Fake("jev", AGREE, remote=True)).decide("s", QS, {"application": "applied"})
        self.assertEqual(d.status("reply"), "act")                 # 0.95 >= degraded 0.95
        self.assertEqual(d.status("stage"), "review")              # 0.90 < degraded 0.95
        self.assertIn("failure", d.rules("stage"))
        self.assertFalse(d.record["backends"]["laya"]["ok"])

    def test_fp2_remote_down(self):
        d = panel(Fake("laya", AGREE), Fake("jev", remote=True, fail=True)).decide("s", QS, {"application": "applied"})
        self.assertEqual(d.results["stage"]["sources"], ["laya"])
        self.assertIn("failure", d.rules("stage"))

    def test_fp3_both_down_never_raises(self):
        d = panel(Fake("laya", fail=True), Fake("jev", remote=True, fail=True)).decide("s", QS)
        self.assertEqual({d.status(q) for q in QS}, {"review"})
        self.assertIsNone(d.results["stage"]["value"])

    def test_fp4_kill_switch_blocks_remote_and_is_recorded(self):
        jev = Fake("jev", AGREE, remote=True)
        d = panel(Fake("laya", AGREE), jev, remote_enabled=False).decide("s", QS, {"application": "applied"})
        self.assertEqual(jev.calls, [])
        self.assertIn("kill_switch", d.record["remote_blocked"])
        self.assertIn("failure", d.rules("stage"))

    def test_fp4_budget_ceiling_blocks_remote(self):
        jev = Fake("jev", AGREE, remote=True)
        d = panel(Fake("laya", AGREE), jev, ledger=Ledger(spend=5.0)).decide("s", QS, {"application": "applied"})
        self.assertEqual(jev.calls, [])
        self.assertIn("economy", d.record["remote_blocked"])

    def test_fp5_no_authorization_stays_local_by_design(self):
        pol = {k: v for k, v in POLICY.items() if k != "remote_authorization"}
        jev = Fake("jev", AGREE, remote=True)
        d = panel(Fake("laya", AGREE), jev, policy=pol).decide("s", QS, {"application": "applied"})
        self.assertEqual(jev.calls, [])
        self.assertEqual(d.status("stage"), "act")                 # not degraded: local-only is the design
        self.assertNotIn("failure", d.rules("stage"))

    def test_fp6_backend_omits_a_question(self):
        partial = {k: v for k, v in AGREE.items() if k != "stage"}
        d = panel(Fake("laya", AGREE), Fake("jev", partial, remote=True)).decide("s", QS, {"application": "applied"})
        self.assertEqual(d.results["stage"]["sources"], ["laya"])
        self.assertIn("failure", d.rules("stage"))

    def test_question_marked_local_is_never_sent(self):
        pol = dict(POLICY, questions=dict(POLICY["questions"], reply={"remote": False}))
        jev = Fake("jev", AGREE, remote=True)
        panel(Fake("laya", AGREE), jev, policy=pol).decide("s", QS, {"application": "applied"})
        self.assertNotIn("reply", jev.calls[0])

    # -- records (§5 economy, §3.1 sovereignty)
    def test_records_carry_no_text_and_log_cost(self):
        ledger = Ledger()
        state = {"subject": "Interview invitation", "body": "secret personal text"}
        panel(Fake("laya", AGREE), Fake("jev", AGREE, remote=True, usage=1000), ledger=ledger).decide(state, QS, {"application": "applied"})
        rec = ledger.decisions[0]
        self.assertNotIn("secret", repr(rec))
        self.assertEqual(len(rec["state_sha256"]), 64)
        self.assertEqual(rec["governance"]["inherits"]["version"], "3.1")
        self.assertEqual(ledger.calls[0]["input_tokens"], 1000)
        self.assertAlmostEqual(ledger.calls[0]["cost_usd"], 1000 * 0.042 / 1e6)

    def test_concurrent_decides_are_independent(self):
        p = panel(Fake("laya", AGREE), Fake("jev", AGREE, remote=True))
        out = []
        ts = [threading.Thread(target=lambda: out.append(p.decide("s", QS, {"application": "applied"}).status("stage"))) for _ in range(8)]
        [t.start() for t in ts]
        [t.join() for t in ts]
        self.assertEqual(out, ["act"] * 8)


if __name__ == "__main__":
    unittest.main()
