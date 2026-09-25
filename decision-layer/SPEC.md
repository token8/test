# Spec: governed parallel decisions (decision panel)

> Status: v1.0, 2026-09-25. Spec → Test → Code: this file is the contract for
> `decision_layer/core/` and `tests/`. Decisions made while coding are written back here.
>
> Inherits from **CoreState OSS: Active Constitution v3.1** (the manifesto). Section
> references (§) point into that document. It is not copied into this public repo.

## 1. Problem

One model's answer isn't a decision. The product asks **several models the same typed
questions in parallel**: Laya locally and TypeSafe Jev hosted, and more later. A
governance layer then turns their votes into one final decision. That layer inherits its
rules from the manifesto, so the decision can be audited against it.

## 2. Flow

```
state + questions + context (current FSM states)
        │
        ├── remote gate (§3.1, §5): authorization recorded? kill switch off? budget left?
        │
        ├──► Laya  (local, Tier 1) ──┐   concurrent; one failing never blocks the other
        └──► Jev   (remote, Tier 2) ─┤
                                     ▼
                 combine votes per question (weighted by question type)
                                     ▼
                 governance rules → status: act | propose | review
                                     ▼
        decision record → logs/decisions.jsonl  (no text; state hash only)
        remote cost     → logs/llm_calls.jsonl  (§5)
```

## 3. Statuses

| Status | Meaning | Who acts |
|---|---|---|
| `act` | Inside the guardrails: models agree, confidence ≥ threshold, legal non-terminal FSM transition, question autonomy `act` | The product, automatically |
| `propose` | Confident, but the manifesto reserves the step for a human (§3.3 Heartbeat): terminal FSM transitions, questions with autonomy `propose`, unknown current state | Human confirms y/N |
| `review` | Not confident: models disagree, confidence below threshold, illegal transition, or no model answered | Human decides |

Precedence: `review` > `propose` > `act`. The strictest status that any rule triggers wins.

## 4. Rules (each result lists the ones that fired, with its § reference)

| Id | Manifesto | Rule |
|---|---|---|
| `sovereignty` | §3.1 Law of Sovereignty | Remote backends get a question only if `remote_authorization` is recorded in the governance file and the question has `remote: true`. Otherwise the question stays local, by design (not degraded). |
| `economy` | §5 Model Routing | Every remote call is logged with tokens and cost. At or above `budget.monthly_usd_ceiling` for the month, remote calls stop (degraded). |
| `kill_switch` | §3, §15 residual | `DECISION_REMOTE=0` stops all remote calls. Each decision record says so, so the switch leaves an auditable trace. |
| `failure` | §2 Testing the Abyss | Degraded mode: an expected backend failed or was blocked. The threshold rises to `degraded_threshold`. |
| `gap` | §1.5 Report the Gap | Backends disagree (when `require_agreement`), or combined confidence is below the threshold → `review`. |
| `state` | §2 State is Sovereign | An answer mapped to an FSM state must be a legal transition from the current state (`context[fsm]`, default `(none)`). Illegal → `review`. Same state → no transition. |
| `heartbeat` | §3.3 Law of the Heartbeat | A transition into an `approval_required` state, or a question with `autonomy: propose` → `propose`. |
| `governor` | §2 Human as System Governor | `act` is granted only when no other rule fired. |

## 5. Combining votes

- Top label: `noul` → `"true"` if P ≥ 0.5, else `"false"`, with probability max(P, 1−P).
  `choice` and `score` → the argmax of `probabilities`.
- Combined distribution: a weighted mean per option over the backends that answered. Weights
  come from `weights[<type>]`, else `weights.default`, else 1.0. A missing option counts as 0.
  The result is renormalised. For `noul`, the weighted mean of P(true).
- `agree` is true when every answering backend has the same top label. It is trivially true
  for one vote.
- Score questions: both backends must use the same probability keys. If they don't,
  agreement fails and the question goes to `review`. This is a known limitation, and the
  failing path is the safe one.

## 6. Failure paths (all tested)

1. Local down, remote up → remote answers alone, degraded threshold.
2. Remote down (error, timeout, 5xx after retries) → local alone, degraded threshold.
3. Both down → every question `review` with reason `no backend answered`. The call never
   raises: the review queue is the failure path.
4. Kill switch or budget reached → remote blocked (degraded), reason recorded.
5. No authorization recorded → remote never called (by design).
6. A backend omits a question → treated as that backend failing for that question.
7. Illegal FSM transition → `review`.
8. Governance file missing or malformed → load fails loudly (no default policy).

## 7. Configuration

- Governance: `<product>/decisions/governance.json` (versioned, reviewed like code).
- Questions: `<product>/decisions/questions.json` (language-neutral; any stack can read it).
- Secrets: `<product>/.env` (git-ignored, §11): `TYPESAFE_API_KEY`, optional `LAYA_URL`,
  `JEV_MODEL`, `DECISION_REMOTE`, `DECISION_LOG_DIR`. Real environment variables win over
  `.env`.

## 8. Layering (§10 Clean Core)

`decision_layer/core/` holds the business logic (combine, rules, orchestration). It uses
only the standard library, with no HTTP or file I/O. Backends and the ledger are passed in as
interfaces. `decision_layer/infrastructure/` holds the HTTP backends, the `.env` loader, the
JSONL ledger and the Laya sidecar.

## 9. Decisions log

- 2026-09-25: The owner authorized sending job-search decision questions to TypeSafe Jev,
  in parallel with Laya (not only as a fallback). This is recorded in `job-crm/decisions/governance.json`.
- 2026-09-25: Jev is classed as Tier 2 (hosted fast inference, about $0.04 per million
  tokens), not Tier 3 frontier. Parallel calls therefore keep `token_economy_ratio` intact.
- 2026-09-25: The cascade client (`decision_layer/client.py`, Laya first and Jev only on doubt)
  is kept as the low-cost mode for products without a remote authorization.
