# Decision layer: Laya and TypeSafe Jev in parallel, governed

A reusable pattern for products that need **decisions, not sentences**: route, classify,
triage and gate text with typed questions and calibrated probabilities.

Several models answer the same typed questions **in parallel**: Laya locally and TypeSafe
Jev hosted. A governance layer turns their votes into one decision, `act`, `propose` or
`review`. It inherits its rules from the CoreState manifesto (Constitution v3.1), and every
decision records which rule fired and why. The contract is [`SPEC.md`](SPEC.md).

```
state + questions + current FSM state
        ├──► Laya (local, ~45 ms)  ─┐
        └──► Jev  (hosted, ~280 ms) ─┤  concurrent; one failing never blocks the other
                                     ▼
          weighted combine → governance rules (§3.1 sovereignty, §3.3 heartbeat,
          §2 FSM, §5 budget, §1.5 report the gap) → act | propose | review
                                     ▼
          logs/decisions.jsonl (no text) · logs/llm_calls.jsonl (tokens, cost)
```

**Why both.** On the same 500 labelled examples ([laya-playground benchmark][bench],
Sept 2026), Laya matches Jev on clear-cut questions (news topic 93% vs 92%, spam 96% vs 96%)
at about a sixth of the latency, for free. Jev is better on nuanced and ordinal questions
(star rating 70% vs 35%; 76% vs 67% overall). When both agree, the decision is solid. When
they disagree, a human looks. Weights per question type lean on whichever model is stronger
for it. Both take the same request (`state`, `questions` of type `choice` / `score` / `noul`).

## Use

```bash
docker compose -f decision-layer/docker/compose.yaml up -d   # laya-serve 0.3.20 on 127.0.0.1:8771
cp job-crm/.env.example job-crm/.env                          # TYPESAFE_API_KEY=...
```

Laya runs as upstream `laya-serve`, which speaks Jev's own protocol (`POST /v1/systemone`), so one
client serves both models. Its router sends each email to the right checkpoint (German to
`multilingual`, English to `english`). The container binds to loopback only, runs read-only as
a non-root user, and caches the weights in a volume. Without Docker, run
`pip install "laya[serve]==0.3.20" && LAYA_HOST=127.0.0.1 LAYA_PORT=8771 LAYA_MODELS=english,multilingual laya-serve`.
Never leave `LAYA_HOST` at its default `0.0.0.0` on a shared network.

```python
from decision_layer.infrastructure import open_panel, load_questions

panel = open_panel("job-crm")        # <product>/.env, decisions/governance.json, logs/
d = panel.decide(state, load_questions("job-crm"), {"application": "applied"})
d.results["stage"]   # {"status": "act", "value": "interview", "probability": 0.93,
                     #  "sources": ["jev", "laya"], "agree": True,
                     #  "transition": {"from": "applied", "to": "interviewing"},
                     #  "rules": {"governor": {"why": ..., "manifesto": "§2 Human as System Governor ..."}}}
```

A product brings two JSON files: `decisions/questions.json` and `decisions/governance.json`.
See [`job-crm/decisions/`](../job-crm/decisions/) for a complete example with thresholds,
weights, a stage FSM, a budget and the recorded remote authorization.

| Setting (`<product>/.env`) | Default | Effect |
|---|---|---|
| `TYPESAFE_API_KEY` | unset | Unset means Laya only |
| `JEV_MODEL` | `jev-latest` | Pin a Jev version for a release |
| `LAYA_URL` | `http://127.0.0.1:8771` | laya-serve (or the fallback `decision_layer.sidecar`) |
| `LAYA_MODEL` | unset | Unset means laya-serve picks the checkpoint per email by language |
| `LAYA_API_KEY` | unset | Bearer token, if laya-serve requires one |
| `JEV_URL` | TypeSafe API | Point at a LiteLLM pass-through or a test double |
| `DECISION_REMOTE` | `1` | `0` is the kill switch: nothing leaves the machine, and each record says so |
| `DECISION_LOG_DIR` | `logs` | Audit trail location inside the product folder |

## Modes

- **Panel** (`decision_layer.core.Panel`, the default): parallel and governed, as above.
- **Cascade** (`decision_layer.client.DecisionClient`): Laya first, and Jev only for
  low-confidence answers. It's cheaper, but has no governance layer. Use it where no remote
  authorization is recorded and cost matters more than a second opinion.

## Evaluate (before letting it act)

```bash
python -m decision_layer.infrastructure.evaluate job-crm job-crm/data/labels.jsonl --out job-crm/data/eval.md
```

Label format and a fictional sample: [`job-crm/decisions/eval/sample.jsonl`](../job-crm/decisions/eval/sample.jsonl).
The report gives accuracy per model and for the panel, the act / propose / review shares, how
often `act` was right, latency, and remote tokens, with a GO / NO-GO per question (defaults:
`act` ≥ 97% right, `review` ≤ 25%). Evaluation calls are real calls and count against the budget.

## Layout

```
decision_layer/core/            combine votes, governance rules, parallel panel: stdlib only, no I/O (§10)
decision_layer/infrastructure/  .env loader, JSONL ledger, open_panel(), evaluate
decision_layer/client.py        HTTP backends (Laya, Jev: same protocol) and the cascade client
decision_layer/sidecar.py       minimal stdlib Laya server, for where laya[serve] can't be installed
docker/                         laya-serve container: loopback, read-only, non-root
```

## Test

```bash
cd decision-layer && python3 -m unittest discover -s tests     # 52 tests, all failure paths in SPEC §6
# the 3 laya-serve contract tests run when laya[serve] is installed, and skip otherwise
```

Laya is by Nandakishor M, Convai Innovations ([Apache-2.0](https://github.com/NandhaKishorM/laya)).
The integration skill is by [brain function collapse](https://brainfunctioncollapse.com/laya).
Jev is a product of [TypeSafe AI](https://typesafe.ai). Neither is affiliated with this repo.

[bench]: https://github.com/wdobry/laya-playground/blob/main/static/data/versus.json
