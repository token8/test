"""Token usage report and spike detection over llm_calls.jsonl."""

import json
import os
import tempfile
import unittest

from decision_layer.infrastructure.usage import daily_usage, main, report


def calls(day, n, tokens=400, cost_per_mtok=0.042):
    return [{"ts": "%sT08:00:00+00:00" % day, "backend": "jev", "input_tokens": tokens,
             "cost_usd": tokens * cost_per_mtok / 1e6} for _ in range(n)]


STEADY = sum((calls("2026-09-%02d" % d, 20) for d in range(15, 25)), [])   # 8,000 tokens a day


class UsageTest(unittest.TestCase):
    def test_daily_totals(self):
        days = {d["day"]: d for d in daily_usage(calls("2026-09-24", 3) + calls("2026-09-25", 2))}
        self.assertEqual((days["2026-09-24"]["calls"], days["2026-09-24"]["input_tokens"]), (3, 1200))
        self.assertEqual(days["2026-09-25"]["calls"], 2)

    def test_steady_day_is_no_spike(self):
        r = report(STEADY + calls("2026-09-25", 22), "2026-09-25", ceiling_usd=5.0)
        self.assertFalse(r["spike"])
        self.assertEqual(r["today"]["input_tokens"], 8800)

    def test_three_times_baseline_is_a_spike(self):
        r = report(STEADY + calls("2026-09-25", 80), "2026-09-25", ceiling_usd=5.0)   # 32,000 vs 8,000
        self.assertTrue(r["spike"])
        self.assertIn("4.0×", r["why"])

    def test_small_absolute_numbers_never_spike(self):
        r = report(calls("2026-09-24", 1) + calls("2026-09-25", 10), "2026-09-25", ceiling_usd=5.0)
        self.assertFalse(r["spike"])                                  # 4,000 tokens is under the floor

    def test_first_heavy_day_without_history_is_a_spike(self):
        r = report(calls("2026-09-25", 100), "2026-09-25", ceiling_usd=5.0)
        self.assertTrue(r["spike"])

    def test_month_to_date_and_ceiling(self):
        r = report(calls("2026-08-31", 5) + calls("2026-09-01", 10, tokens=10_000_000), "2026-09-25", ceiling_usd=5.0)
        self.assertEqual(r["month"]["input_tokens"], 100_000_000)
        self.assertAlmostEqual(r["month"]["ceiling_used"], 4.2 / 5.0)

    def test_cli_exit_code_on_spike(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "logs"))
            with open(os.path.join(d, "logs", "llm_calls.jsonl"), "w") as f:
                for rec in STEADY + calls("2026-09-25", 80):
                    f.write(json.dumps(rec) + "\n")
            self.assertEqual(main([d, "--today", "2026-09-25"]), 0)
            self.assertEqual(main([d, "--today", "2026-09-25", "--fail-on-spike"]), 1)

    def test_cli_without_log_is_fine(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(main([d, "--fail-on-spike"]), 0)


if __name__ == "__main__":
    unittest.main()
