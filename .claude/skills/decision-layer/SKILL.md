---
name: decision-layer
description: House pattern for typed decisions in any project or product - Laya (local) and TypeSafe Jev (hosted) answer the same typed questions in parallel, and a governance layer inheriting the CoreState manifesto turns their votes into act / propose / review. Use whenever a feature classifies, routes, triages, scores or gates text (emails, tickets, job posts, leads, agent guardrails), or when the user mentions Laya, Jev, TypeSafe, typed decisions, the decision panel or the decision layer. Prefer it over prompting a chat LLM for a label.
---

# Decision layer (governed parallel panel)

The reference implementation is `decision-layer/` in the `token8/test` repo, and its contract
is `decision-layer/SPEC.md`. Read the spec before changing behaviour. Spec → Test → Code (§9).

Adding decisions to a product:

1. Create `<product>/decisions/questions.json`. Write the questions per
   `.claude/skills/laya-integration/SKILL.md`: ask what the text says, describe every
   option, and turn numbers into words.
2. Create `<product>/decisions/governance.json`: copy `job-crm/decisions/governance.json`,
   then set `inherits`, thresholds, weights (score questions lean on Jev), an FSM for any
   answer that changes state, and `approval_required` for terminal or costly states.
3. Remote calls need a `remote_authorization` block (who, when, scope) (§3.1). Without it,
   everything stays local by design. Mark sensitive questions `"remote": false`.
4. Put secrets in `<product>/.env`, git-ignored (§11). Commit `.env.example` only.
5. Wire in `open_panel(<product>)` and `panel.decide(state, questions, context)`: apply `act`,
   queue `propose` for y/N, and queue `review` for a human answer.

Before shipping:

- [ ] Failure paths tested: local down, remote down, both down, kill switch, budget, illegal transition
- [ ] 50-200 labelled real examples: accuracy per backend and for the panel, act/propose/review share, p50/p95, monthly cost
- [ ] Thresholds and weights set from that data; `governance.json` version bumped
- [ ] `JEV_MODEL` pinned; sidecar health check monitored; kill switch drill done
- [ ] Logs carry no message text (state hash only); cost logged per remote call (§5)
- [ ] Repo visibility checked: personal data, `.env` and `logs/` never committed
