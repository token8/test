"""Remote token usage from <product>/logs/llm_calls.jsonl: per day, month to date, and spikes (§5).

    python -m decision_layer.infrastructure.usage <product>                  # prints the report
    python -m decision_layer.infrastructure.usage <product> --fail-on-spike  # exit 1 on a spike (for runs)

A spike is a day whose input tokens reach `factor` × the median of the previous `window`
days (days without calls count as 0) and at least `min_tokens`, so small absolute numbers
never alarm. The monthly budget ceiling comes from <product>/decisions/governance.json.
"""

import argparse
import json
import os
import statistics
import sys
from datetime import date, timedelta

FACTOR, WINDOW, MIN_TOKENS = 3.0, 7, 20_000


def daily_usage(records):
    days = {}
    for r in records:
        d = days.setdefault(r.get("ts", "")[:10], {"calls": 0, "input_tokens": 0, "cost_usd": 0.0})
        d["calls"] += 1
        d["input_tokens"] += r.get("input_tokens") or 0
        d["cost_usd"] += r.get("cost_usd") or 0.0
    return [{"day": k, **v} for k, v in sorted(days.items())]


def report(records, today, ceiling_usd=None, factor=FACTOR, window=WINDOW, min_tokens=MIN_TOKENS):
    by_day = {d["day"]: d for d in daily_usage(records)}
    empty = {"calls": 0, "input_tokens": 0, "cost_usd": 0.0}
    t = date.fromisoformat(today)
    prior = [by_day.get((t - timedelta(days=i)).isoformat(), empty)["input_tokens"] for i in range(1, window + 1)]
    baseline = statistics.median(prior)
    now = by_day.get(today, {"day": today, **empty})
    ratio = now["input_tokens"] / baseline if baseline else float("inf") if now["input_tokens"] else 0.0
    spike = now["input_tokens"] >= min_tokens and ratio >= factor
    month = [d for k, d in by_day.items() if k[:7] == today[:7]]
    m_cost = sum(d["cost_usd"] for d in month)
    return {
        "today": {"day": today, "calls": now["calls"], "input_tokens": now["input_tokens"], "cost_usd": now["cost_usd"]},
        "baseline_tokens": baseline,
        "spike": spike,
        "why": ("%s tokens today = %s× the %d-day median of %s" % (
            f"{now['input_tokens']:,}", "∞" if ratio == float("inf") else "%.1f" % ratio, window, f"{baseline:,.0f}"))
               if spike else "within normal range",
        "month": {"input_tokens": sum(d["input_tokens"] for d in month), "cost_usd": m_cost,
                  "ceiling_usd": ceiling_usd, "ceiling_used": (m_cost / ceiling_usd) if ceiling_usd else None},
    }


def render(r):
    m, t = r["month"], r["today"]
    lines = ["Remote token usage (Jev)",
             "  today %s: %d calls, %s input tokens, $%.4f" % (t["day"], t["calls"], f"{t['input_tokens']:,}", t["cost_usd"]),
             "  month to date: %s input tokens, $%.4f%s" % (
                 f"{m['input_tokens']:,}", m["cost_usd"],
                 " (%.1f%% of the $%.2f ceiling)" % (100 * m["ceiling_used"], m["ceiling_usd"]) if m["ceiling_usd"] else ""),
             ("  SPIKE: " if r["spike"] else "  ") + r["why"]]
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("product")
    ap.add_argument("--today", default=date.today().isoformat())
    ap.add_argument("--fail-on-spike", action="store_true")
    ap.add_argument("--factor", type=float, default=FACTOR)
    ap.add_argument("--min-tokens", type=int, default=MIN_TOKENS)
    args = ap.parse_args(argv)

    log = os.path.join(args.product, os.environ.get("DECISION_LOG_DIR", "logs"), "llm_calls.jsonl")
    records = []
    if os.path.exists(log):
        with open(log) as f:
            records = [json.loads(line) for line in f if line.strip()]
    ceiling = None
    gov = os.path.join(args.product, "decisions", "governance.json")
    if os.path.exists(gov):
        with open(gov) as f:
            ceiling = json.load(f).get("budget", {}).get("monthly_usd_ceiling")
    r = report(records, args.today, ceiling, factor=args.factor, min_tokens=args.min_tokens)
    sys.stdout.write(render(r))
    return 1 if args.fail_on_spike and r["spike"] else 0


if __name__ == "__main__":
    sys.exit(main())
