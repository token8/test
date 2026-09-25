---
name: decision-layer
description: House pattern for typed decisions in any project or product - Laya running locally as the primary model, TypeSafe Jev as the hosted fallback. Use whenever a feature classifies, routes, triages, scores or gates text (emails, tickets, job posts, leads, agent guardrails), or when the user mentions Laya, Jev, TypeSafe, typed decisions or the decision layer. Prefer it over prompting a chat LLM for a label.
---

# Decision layer (Laya → Jev)

The reference implementation is `decision-layer/` in the `token8/test` repo. Copy or vendor
`decision_layer/` (standard library only), or reimplement `DecisionClient.decide` in the
project's language, with the same order of steps:

1. Ask Laya (loopback sidecar) all questions in **one** call.
2. Escalate a question when Laya failed, its top probability is below the question's
   `min_confidence`, or its type is in `always_remote` (default: `score`).
3. Send only escalated questions with `allow_remote=True` to Jev (`POST
   https://api.typesafe.ai/v1/systemone`, `Authorization: Bearer $TYPESAFE_API_KEY`, body
   `{state, model, questions}`), with short retries on 429/5xx.
4. Return answers plus, per question, the source (`laya`/`jev`), and list the escalated
   questions and the ones no backend could answer confidently (these go to a human).

Before shipping a feature that uses it:

- [ ] Questions written per `.claude/skills/laya-integration/SKILL.md` (ask what the text says; described options; numbers turned into words)
- [ ] Privacy decided per question: `allow_remote=False` for personal data not cleared for TypeSafe; `DECISION_REMOTE_FALLBACK=0` kill switch wired
- [ ] 50-200 labelled real examples; accuracy per backend, escalation rate and p50/p95 latency recorded in the release notes
- [ ] Thresholds chosen from that data; low-confidence path goes to a person or a review queue
- [ ] `JEV_MODEL` pinned for the release; sidecar health check in the app's startup/monitoring
- [ ] Metrics logged without the text: sources, escalations, timings, Jev input tokens
