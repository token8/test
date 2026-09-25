"""Typed decisions: Laya first (local), TypeSafe Jev as the fallback (hosted).

Both models take the same request, a `state` (the text) plus a dict of typed questions
(`choice`, `score`, `noul`), and return `{"answers": {id: {...probabilities...}}}`. So one
question set works on both, and the fallback is a routing decision, not a translation.

    client = DecisionClient.from_env()
    res = client.decide(state, questions)
    res.answers["stage"]["choice"], res.sources["stage"]   # -> "interview", "laya"

A question goes to Jev when Laya is down, when Laya's top probability is below the
question's threshold, or when its type is listed in `always_remote` (Laya is weak on
ordinal `score` questions). Questions marked `allow_remote=False` never leave the machine.
Standard library only, so it drops into any Python project.
"""

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

JEV_URL = "https://api.typesafe.ai/v1/systemone"
LAYA_URL = "http://127.0.0.1:8771"


class BackendError(RuntimeError):
    pass


@dataclass(frozen=True)
class Policy:
    """When to trust Laya for one question, and whether it may be sent to Jev at all."""
    min_confidence: float = 0.85   # Laya's top probability must reach this to be kept
    allow_remote: bool = True      # False: never send this question (and its state) to Jev


@dataclass
class Decision:
    answers: dict
    sources: dict                  # question id -> "laya" | "jev"
    escalated: list = field(default_factory=list)   # ids Laya answered too weakly or not at all
    fallback_failed: list = field(default_factory=list)  # escalated ids Jev could not answer
    timings_ms: dict = field(default_factory=dict)


def top_probability(answer):
    """Probability of the answer's winning option, comparable across question types."""
    if answer.get("type") == "noul" or ("noul" in answer and "probabilities" not in answer):
        p = float(answer["noul"])
        return max(p, 1 - p)
    return max(float(v) for v in answer["probabilities"].values())


def _post(url, body, headers, timeout):
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json", **headers})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise BackendError("%s %s: %s" % (url, e.code, e.read()[:300].decode("utf-8", "replace"))) from e
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise BackendError("%s: %s" % (url, e)) from e


class LayaHTTP:
    """Laya running as a loopback sidecar (see sidecar.py)."""
    name, remote = "laya", False

    def __init__(self, url=LAYA_URL, timeout=2.0):
        self.url, self.timeout = url.rstrip("/"), timeout

    def predict(self, state, questions):
        return _post(self.url + "/predict", {"state": state, "questions": questions}, {}, self.timeout)


class Jev:
    """TypeSafe's hosted Jev. Retries briefly on rate limits and 5xx, then gives up."""
    name, remote = "jev", True
    RETRY = {429, 500, 502, 503, 504, 529}

    def __init__(self, api_key, model="jev-latest", url=JEV_URL, timeout=5.0, retries=2):
        self.api_key, self.model, self.url, self.timeout, self.retries = api_key, model, url, timeout, retries

    def predict(self, state, questions):
        body = {"state": state, "model": self.model, "questions": questions}
        for attempt in range(self.retries + 1):
            try:
                return _post(self.url, body, {"Authorization": "Bearer " + self.api_key}, self.timeout)
            except BackendError as e:
                code = getattr(e.__cause__, "code", None)
                if attempt == self.retries or (code is not None and code not in self.RETRY):
                    raise
                time.sleep(0.5 * 2 ** attempt)


class DecisionClient:
    def __init__(self, primary, fallback=None, default_policy=Policy(), always_remote=("score",)):
        self.primary, self.fallback = primary, fallback
        self.default_policy, self.always_remote = default_policy, frozenset(always_remote)

    @classmethod
    def from_env(cls, **kw):
        """LAYA_URL, TYPESAFE_API_KEY, JEV_MODEL; DECISION_REMOTE=0 turns Jev off."""
        key = os.environ.get("TYPESAFE_API_KEY")
        remote = os.environ.get("DECISION_REMOTE", os.environ.get("DECISION_REMOTE_FALLBACK", "1")) != "0"
        fallback = Jev(key, model=os.environ.get("JEV_MODEL", "jev-latest")) if key and remote else None
        return cls(LayaHTTP(os.environ.get("LAYA_URL", LAYA_URL)), fallback, **kw)

    def decide(self, state, questions, policies=None):
        policies = policies or {}
        policy = lambda qid: policies.get(qid, self.default_policy)
        answers, sources, timings = {}, {}, {}

        t0 = time.perf_counter()
        try:
            answers = dict(self.primary.predict(state, questions)["answers"])
            sources = {qid: self.primary.name for qid in answers}
        except BackendError:
            pass                                   # every question escalates below
        timings[self.primary.name] = (time.perf_counter() - t0) * 1000

        escalated = [
            qid for qid, q in questions.items()
            if qid not in answers
            or q.get("type") in self.always_remote
            or top_probability(answers[qid]) < policy(qid).min_confidence
        ]
        remote = [qid for qid in escalated if policy(qid).allow_remote]

        failed = [qid for qid in escalated if qid not in remote]
        if remote and self.fallback:
            t0 = time.perf_counter()
            try:
                got = self.fallback.predict(state, {qid: questions[qid] for qid in remote})["answers"]
                for qid in remote:
                    if qid in got:
                        answers[qid], sources[qid] = got[qid], self.fallback.name
                    else:
                        failed.append(qid)
            except BackendError:
                failed += remote
            timings[self.fallback.name] = (time.perf_counter() - t0) * 1000
        else:
            failed += remote

        missing = [qid for qid in questions if qid not in answers]
        if missing:
            raise BackendError("no backend answered: %s" % ", ".join(missing))
        return Decision(answers, sources, escalated, failed, timings)
