"""Evaluate a product's decision panel on labelled examples (release checklist step 3).

    python -m decision_layer.infrastructure.evaluate <product> <product>/data/labels.jsonl --out <product>/data/eval.md

labels.jsonl, one example per line (keep it in the git-ignored data/ folder, it holds real mail):
    {"id": "m-001", "state": {"subject": "...", "body": "..."}, "context": {"application": "applied"},
     "labels": {"stage": "interview", "needs_reply": true, "urgency": 2}}

Reports, per question: accuracy of each backend alone and of the panel, the act / propose /
review shares, how often `act` was right (what go/no-go hinges on), and p50/p95 latency.
Remote calls are real calls: they are logged and count against the monthly budget (§5).
The report carries ids and numbers only, never message text.
"""

import argparse
import json
import sys

from ..core import combine


def normalise_label(label):
    if isinstance(label, bool):
        return "true" if label else "false"
    return str(label)


def _pct(values, q):
    if not values:
        return None
    values = sorted(values)
    return round(values[min(len(values) - 1, int(q * (len(values) - 1) + 0.5))], 1)


def evaluate(panel, questions, examples):
    remote = {b.name for b in panel.backends if b.remote}
    names = [b.name for b in panel.backends]
    rows = {qid: [] for qid in questions}
    latency = {name: [] for name in names}
    tokens = 0

    for ex in examples:
        d = panel.decide(ex["state"], questions, ex.get("context"))
        for name, b in d.record["backends"].items():
            if b.get("ok"):
                latency[name].append(b["ms"])
                if name in remote:
                    tokens += b.get("input_tokens") or 0
        for qid, label in ex.get("labels", {}).items():
            if qid not in questions:
                continue
            gold, r = normalise_label(label), d.results[qid]
            rows[qid].append({
                "gold": gold,
                "panel": r["value"],
                "status": r["status"],
                "backends": {n: combine({n: a}, {})["value"] for n, a in d.votes.get(qid, {}).items()},
            })

    report = {"examples": len(examples), "remote_input_tokens": tokens, "questions": {},
              "latency_ms": {n: {"p50": _pct(v, 0.5), "p95": _pct(v, 0.95)} for n, v in latency.items()}}
    for qid, rs in rows.items():
        n = len(rs)
        acc = lambda pred: round(sum(pred(r) == r["gold"] for r in rs) / n, 4) if n else None
        acted = [r for r in rs if r["status"] == "act"]
        report["questions"][qid] = {
            "n": n,
            "accuracy": {**{name: acc(lambda r, name=name: r["backends"].get(name)) for name in names},
                         "panel": acc(lambda r: r["panel"])},
            "status": {s: (round(sum(r["status"] == s for r in rs) / n, 4) if n else None) for s in ("act", "propose", "review")},
            "act_accuracy": round(sum(r["panel"] == r["gold"] for r in acted) / len(acted), 4) if acted else None,
        }
    return report


def go_no_go(report, min_act_accuracy=0.97, max_review_share=0.25):
    out = {}
    for qid, q in report["questions"].items():
        if not q["n"]:
            out[qid] = {"go": False, "why": "no labelled examples"}
        elif q["act_accuracy"] is not None and q["act_accuracy"] < min_act_accuracy:
            out[qid] = {"go": False, "why": "act decisions %.0f%% right < %.0f%%" % (100 * q["act_accuracy"], 100 * min_act_accuracy)}
        elif q["status"]["review"] > max_review_share:
            out[qid] = {"go": False, "why": "review share %.0f%% > %.0f%%" % (100 * q["status"]["review"], 100 * max_review_share)}
        else:
            out[qid] = {"go": True, "why": "within thresholds"}
    return out


def render_markdown(report, verdict):
    names = [n for n in next(iter(report["questions"].values()), {"accuracy": {}})["accuracy"] if n != "panel"]
    f = lambda v: "–" if v is None else "%.0f%%" % (100 * v)
    head = "| Question | n | " + " | ".join("%s acc." % n for n in names) + " | Panel acc. | act / propose / review | act right | Verdict |"
    lines = [head, "|" + "---|" * (head.count("|") - 1)]
    for qid, q in report["questions"].items():
        s, v = q["status"], verdict[qid]
        lines.append("| %s | %d | %s | %s | %s / %s / %s | %s | %s: %s |" % (
            qid, q["n"], " | ".join(f(q["accuracy"][n]) for n in names), f(q["accuracy"]["panel"]),
            f(s["act"]), f(s["propose"]), f(s["review"]), f(q["act_accuracy"]), "GO" if v["go"] else "NO-GO", v["why"]))
    lines.append("")
    lines.append("Latency p50/p95 ms: " + ", ".join("%s %s/%s" % (n, l["p50"], l["p95"]) for n, l in report["latency_ms"].items()))
    lines.append("Examples: %d · remote input tokens: %d" % (report["examples"], report["remote_input_tokens"]))
    return "\n".join(lines) + "\n"


def main(argv=None):
    from . import load_questions, open_panel

    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("product"), ap.add_argument("labels")
    ap.add_argument("--out", help="write the markdown report here (keep it in data/ if ids are sensitive)")
    ap.add_argument("--min-act-accuracy", type=float, default=0.97)
    ap.add_argument("--max-review-share", type=float, default=0.25)
    args = ap.parse_args(argv)

    with open(args.labels) as fh:
        examples = [json.loads(line) for line in fh if line.strip()]
    report = evaluate(open_panel(args.product), load_questions(args.product), examples)
    md = render_markdown(report, go_no_go(report, args.min_act_accuracy, args.max_review_share))
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(md)
    sys.stdout.write(md)


if __name__ == "__main__":
    main()
