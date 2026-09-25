# Decision layer: Laya first, TypeSafe Jev as fallback

A reusable pattern for products that need **decisions, not sentences**: route, classify,
triage and gate text with typed questions and calibrated probabilities, instead of
prompting a chat LLM and parsing its prose.

```
            state + typed questions
                     │
                     ▼
     ┌───────────────────────────────┐
     │ Laya (local sidecar, ~20-60ms)│  open weights, Apache-2.0, no data leaves the machine
     └───────────────┬───────────────┘
      confident?     │  no / Laya down / type in always_remote
        │ yes        ▼
        │   ┌─────────────────────────────┐
        │   │ Jev (TypeSafe API, ~280 ms) │  only questions with allow_remote=True
        │   └──────────────┬──────────────┘
        ▼                  ▼
   answers + per-question source ("laya" | "jev") + escalated / fallback_failed
```

**Why this order.** On the same 500 labelled examples ([laya-playground benchmark][bench],
Sept 2026) Laya matches Jev on clear-cut questions (news topic 93% vs 92%, SMS spam 96% vs
96%) at about a sixth of the latency and no cost. Jev is clearly better on nuanced and ordinal
questions (star rating 70% vs 35%, overall 76% vs 67%, better calibrated). So Laya takes the
traffic and Jev catches what Laya is unsure about. The escalation rate is the number to watch:
it is what you pay Jev latency and money on (about $0.04 per million input tokens).

Both models take the same request (`state`, `questions` of type `choice` / `score` / `noul`)
and return the same `answers` shape. One question set therefore works on both.

## Use

```bash
pip install laya                                  # on the machine that runs the sidecar
python -m decision_layer.sidecar                  # Laya on 127.0.0.1:8771, warmed up
export TYPESAFE_API_KEY=...                       # optional: enables the Jev fallback
```

```python
from decision_layer import DecisionClient
from decision_layer.presets import job_email_questions, JOB_EMAIL_POLICIES

client = DecisionClient.from_env()
res = client.decide({"subject": subject, "body": body}, job_email_questions(), JOB_EMAIL_POLICIES)
res.answers["stage"]["choice"]     # "interview"
res.sources                        # {"stage": "laya", "needs_reply": "laya", "urgency": "jev"}
res.fallback_failed                # escalated but no better answer: send to a human
```

| Setting | Default | Effect |
|---|---|---|
| `LAYA_URL` | `http://127.0.0.1:8771` | Laya sidecar |
| `LAYA_CHECKPOINT` | English | `multilingual` for non-English text (uncalibrated) |
| `TYPESAFE_API_KEY` | unset | Unset means no fallback: weak answers are flagged, not escalated |
| `JEV_MODEL` | `jev-latest` | Pin a Jev version for reproducible releases |
| `DECISION_REMOTE_FALLBACK` | `1` | `0` is a kill switch: nothing goes to TypeSafe |
| `Policy(min_confidence)` | 0.85 | Per question; set from labelled data, not by feel |
| `Policy(allow_remote)` | `True` | `False` for questions over personal data that must stay local |
| `always_remote` | `("score",)` | Types sent straight to Jev (Laya is weakest on ordinal scores) |

## Rules

- **Privacy.** A fallback sends the whole `state` to a third party. Default to
  `allow_remote=False` wherever the state holds personal data you have not cleared for that.
- **Measure before trusting.** 50-200 real labelled examples per question set. Record accuracy
  per backend, and the escalation rate. Tune thresholds from them. See
  [`.claude/skills/laya-integration`](../.claude/skills/laya-integration/SKILL.md).
- **Ask what the text says**, map to actions in code, and turn numbers into words first.
- **Log the source**, never the text: `res.sources`, `res.escalated` and timings are the metrics.

## Test

```bash
cd decision-layer && python3 -m unittest discover -s tests
```

Standard library only. `sidecar.py` is the only file that needs `laya`.

Laya is by Nandakishor M, Convai Innovations ([Apache-2.0](https://github.com/NandhaKishorM/laya)).
The integration skill is by [brain function collapse](https://brainfunctioncollapse.com/laya).
Jev is a product of [TypeSafe AI](https://typesafe.ai). Neither is affiliated with this repo.

[bench]: https://github.com/wdobry/laya-playground/blob/main/static/data/versus.json
