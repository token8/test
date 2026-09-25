"""Governance: turns combined votes into act / propose / review, citing the manifesto (SPEC.md §3-5).

Pure business logic (§10 Clean Core): no I/O, no vendor code. The policy is a dict, loaded
from `<product>/decisions/governance.json` by the infrastructure layer.
"""

RULES = {
    "sovereignty": "§3.1 Law of Sovereignty: data leaves the machine only under a recorded authorization",
    "economy": "§5 Model Routing: remote calls logged with cost, stopped at the monthly ceiling",
    "kill_switch": "§3 kill switch: DECISION_REMOTE=0 stops all remote calls, recorded per decision",
    "failure": "§2 Testing the Abyss: degraded mode raises the bar",
    "gap": "§1.5 Report the Gap: disagreement or low confidence is not a decision",
    "state": "§2 State is Sovereign: only modelled FSM transitions",
    "heartbeat": "§3.3 Law of the Heartbeat: the agent proposes, the human disposes",
    "governor": "§2 Human as System Governor: autonomy only within the guardrails",
}
RANK = {"act": 0, "propose": 1, "review": 2}
NO_STATE = "(none)"


class GovernanceError(ValueError):
    pass


def _top(answer):
    if answer.get("type") == "noul" or ("noul" in answer and "probabilities" not in answer):
        p = float(answer["noul"])
        return {"true": p, "false": 1 - p}
    return {str(k): float(v) for k, v in answer["probabilities"].items()}


def combine(votes, weights):
    """votes: {backend: answer}. Weighted mean distribution, winner, and whether all backends agree."""
    dists = {name: _top(a) for name, a in votes.items()}
    total = sum(weights.get(name, 1.0) for name in dists)
    labels = sorted({k for d in dists.values() for k in d})
    mixed = {k: sum(weights.get(n, 1.0) * d.get(k, 0.0) for n, d in dists.items()) / total for k in labels}
    norm = sum(mixed.values()) or 1.0
    mixed = {k: v / norm for k, v in mixed.items()}
    value = max(mixed, key=mixed.get)
    tops = {max(d, key=d.get) for d in dists.values()}
    return {"value": value, "probability": mixed[value], "probabilities": mixed, "agree": len(tops) == 1}


class Governance:
    def __init__(self, policy):
        for key in ("version", "inherits", "defaults", "questions"):
            if key not in policy:
                raise GovernanceError("governance policy is missing %r" % key)
        self.policy = policy
        self.version, self.inherits = policy["version"], policy["inherits"]
        self.authorization = policy.get("remote_authorization")
        self.budget = policy.get("budget", {})
        self.fsm = policy.get("fsm", {})
        for qid in policy["questions"]:
            cfg = self.question(qid)
            if cfg["autonomy"] not in ("act", "propose"):
                raise GovernanceError("%s: autonomy must be 'act' or 'propose'" % qid)
            if cfg.get("fsm") and cfg["fsm"] not in self.fsm:
                raise GovernanceError("%s: unknown fsm %r" % (qid, cfg["fsm"]))

    def question(self, qid):
        return {**self.policy["defaults"], **self.policy["questions"].get(qid, {})}

    def weights(self, qtype):
        w = self.policy.get("weights", {})
        return w.get(qtype, w.get("default", {}))

    def price(self, backend):
        return self.budget.get("price_per_mtok", {}).get(backend, 0.0)

    def remote_allowed(self, qid):
        return bool(self.authorization) and bool(self.question(qid).get("remote", True))

    def decide(self, qid, qtype, votes, degraded, context):
        """-> result dict. `degraded`: names of expected backends that did not answer."""
        cfg, fired = self.question(qid), {}
        status = "act"

        def fire(rule, level, why):
            nonlocal status
            fired[rule] = why
            if RANK[level] > RANK[status]:
                status = level

        if not votes:
            fire("failure", "review", "no backend answered")
            return self._result(status, None, None, [], False, None, fired)

        c = combine(votes, self.weights(qtype))
        threshold = cfg["act_threshold"]
        if degraded:
            threshold = max(threshold, cfg["degraded_threshold"])
            fire("failure", "act", "%s missing; threshold raised to %.2f" % (", ".join(sorted(degraded)), threshold))
        if cfg["require_agreement"] and not c["agree"]:
            fire("gap", "review", "backends disagree")
        if c["probability"] < threshold:
            fire("gap", "review", "confidence %.2f below %.2f" % (c["probability"], threshold))

        transition = None
        if cfg.get("fsm"):
            fsm = self.fsm[cfg["fsm"]]
            target = fsm.get("map", {}).get(c["value"])
            current = (context or {}).get(cfg["fsm"]) or NO_STATE
            if target and target != current:
                transition = {"from": current, "to": target}
                if target not in fsm.get("transitions", {}).get(current, []):
                    fire("state", "review", "%s -> %s is not a modelled transition" % (current, target))
                elif target in fsm.get("approval_required", []):
                    fire("heartbeat", "propose", "entering %s needs human approval" % target)
        if cfg["autonomy"] == "propose":
            fire("heartbeat", "propose", "question autonomy is 'propose'")
        if not fired:
            fired["governor"] = "inside the guardrails"
        return self._result(status, c["value"], c["probability"], sorted(votes), c["agree"], transition, fired)

    @staticmethod
    def _result(status, value, probability, sources, agree, transition, fired):
        return {"status": status, "value": value, "probability": probability, "sources": sources,
                "agree": agree, "transition": transition,
                "rules": {r: {"why": why, "manifesto": RULES[r]} for r, why in fired.items()}}
