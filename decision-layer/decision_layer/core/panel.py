"""Decision panel: ask every backend in parallel, then let governance decide (SPEC.md §2).

Backends are anything with `name`, `remote` (bool) and `predict(state, questions) -> {"answers": ...}`.
The ledger has `spend_this_month()`, `record_call(dict)` and `record_decision(dict)`.
Neither is imported here (§10 Clean Core): the infrastructure layer passes them in.
"""

import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Decision:
    results: dict      # qid -> {status, value, probability, sources, agree, transition, rules}
    record: dict       # what went to the audit log
    votes: dict = field(default_factory=dict)   # qid -> {backend: raw answer}; in memory only, never logged

    def status(self, qid):
        return self.results[qid]["status"]

    def rules(self, qid):
        return self.results[qid]["rules"]


class Panel:
    def __init__(self, backends, governance, ledger, remote_enabled=True):
        self.backends, self.gov, self.ledger, self.remote_enabled = list(backends), governance, ledger, remote_enabled

    def _remote_blocked(self):
        """Reasons remote backends may not be called right now, beyond per-question authorization."""
        blocked = {}
        if not self.remote_enabled:
            blocked["kill_switch"] = "DECISION_REMOTE=0"
        ceiling = self.gov.budget.get("monthly_usd_ceiling")
        if ceiling is not None and self.ledger.spend_this_month() >= ceiling:
            blocked["economy"] = "monthly ceiling of $%.2f reached" % ceiling
        return blocked

    def _call(self, backend, state, questions):
        t0 = time.perf_counter()
        try:
            res = backend.predict(state, questions)
            return {"ok": True, "answers": res.get("answers", {}), "model": res.get("model"),
                    "input_tokens": (res.get("usage") or {}).get("input_tokens"),
                    "ms": round((time.perf_counter() - t0) * 1000, 1)}
        except Exception as e:                      # any backend failure is a mapped path, never a crash
            return {"ok": False, "answers": {}, "error": "%s: %s" % (type(e).__name__, e),
                    "ms": round((time.perf_counter() - t0) * 1000, 1)}

    def decide(self, state, questions, context=None):
        blocked = self._remote_blocked()
        # which backends each question is designed to reach (sovereignty), and which may be called now
        expected = {qid: [b.name for b in self.backends if not b.remote or self.gov.remote_allowed(qid)]
                    for qid in questions}
        plan = {}
        for b in self.backends:
            qs = {qid: q for qid, q in questions.items() if b.name in expected[qid]}
            if qs and not (b.remote and blocked):
                plan[b.name] = (b, qs)

        with ThreadPoolExecutor(max_workers=max(1, len(plan))) as pool:
            futures = {name: pool.submit(self._call, b, state, qs) for name, (b, qs) in plan.items()}
            calls = {name: f.result() for name, f in futures.items()}

        results, all_votes = {}, {}
        for qid, q in questions.items():
            votes = all_votes[qid] = {name: c["answers"][qid] for name, c in calls.items() if qid in c["answers"]}
            degraded = [name for name in expected[qid] if name not in votes]
            results[qid] = self.gov.decide(qid, q.get("type"), votes, degraded, context)

        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        for name, c in calls.items():
            if plan[name][0].remote and c["ok"]:
                tokens = c.get("input_tokens") or 0
                self.ledger.record_call({"ts": now, "backend": name, "model": c.get("model"), "input_tokens": tokens,
                                         "cost_usd": tokens * self.gov.price(name) / 1e6, "task": "typed-decision"})
        record = {
            "ts": now,
            "governance": {"version": self.gov.version, "inherits": self.gov.inherits},
            "state_sha256": hashlib.sha256(json.dumps(state, sort_keys=True, default=str).encode()).hexdigest(),
            "context": context or {},
            "remote_blocked": blocked,
            "backends": {name: {k: v for k, v in c.items() if k != "answers"} for name, c in calls.items()},
            "results": {qid: {k: r[k] for k in ("status", "value", "probability", "sources", "transition")}
                        | {"rules": sorted(r["rules"])} for qid, r in results.items()},
        }
        self.ledger.record_decision(record)
        return Decision(results, record, all_votes)
