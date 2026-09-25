# Job search CRM: next release plan (governed decision panel)

> Status: **planning**. Started 2026-09-25. This file is the release checklist; tick items in
> the same commit that completes them, so the history shows who closed what and when.
> Governed by **CoreState OSS: Active Constitution v3.1** (the manifesto). § references point there.

## Goal

Ship a release where the CRM files and prioritises job-search mail by itself. **Laya
(local) and TypeSafe Jev (hosted) answer the same typed questions in parallel**, and a
governance layer turns their votes into one decision. That layer inherits from the
manifesto ([spec](../decision-layer/SPEC.md)):

- `act`: the CRM does it (models agree, confident, a legal non-terminal stage change)
- `propose`: a human confirms y/N (offer, rejection, acceptance, withdrawal: §3.3 Heartbeat)
- `review`: a human decides (disagreement, low confidence, illegal transition, models down)

## Scope

| Feature | Question (`job-crm/decisions/questions.json`) | Governance (`governance.json`) |
|---|---|---|
| File inbound email to the application's stage | `stage` (choice) | Agreement + ≥ 0.80. Stage change must be a modelled FSM transition. Terminal states need approval |
| "Needs reply" flag on the dashboard | `needs_reply` (yes/no) | Agreement + ≥ 0.90 |
| Urgency sort of the inbox | `urgency` (score) | Weighted Jev 1.5 : Laya 0.5 (Laya is weak on scores), ≥ 0.60 |
| Review and approval queue | everything `propose` / `review` | Human |

Out of scope for this release: generating replies, extracting values (salary, dates), job-post
fit scoring (next release), and fine-tuning Laya.

## Checklist

### 0. Setup
- [x] Evaluate Laya against Jev (500 examples: Laya 67% / Jev 76% overall, level on simple questions, about 6× faster, free)
- [x] Laya integration skill vendored to `.claude/skills/laya-integration/`; house skill `.claude/skills/decision-layer/`
- [x] Manifesto located (Drive: `manifesto.md`, Constitution v3.1) and mapped to decision rules (spec §4)
- [x] Spec written first: `decision-layer/SPEC.md` (§9 SDD)
- [x] Tests with every failure path: 45 passing (`decision-layer/tests/`)
- [x] Parallel panel + governance in `decision_layer/core/` (no vendor code, §10); HTTP, `.env` and ledger in `infrastructure/`
- [x] CRM home created: `job-crm/` with `decisions/questions.json`, `decisions/governance.json`, `.env.example`, `.gitignore`
- [x] Remote authorization for TypeSafe recorded in `governance.json` (owner, 2026-09-25, §3.1)
- [ ] **Check the CRM code into `job-crm/`** (see "Where the code goes" in `job-crm/README.md`). Note: this repo is **public**
- [ ] Decide the release version number and target date

### 1. Decisions
- [x] TypeSafe is called in parallel, not only as fallback (owner, 2026-09-25)
- [x] API key lives in `job-crm/.env`, git-ignored (§11)
- [ ] Create `job-crm/.env` from `.env.example` with the TypeSafe key; rotate quarterly
- [ ] Where the Laya sidecar runs (laptop, home server, VM), and which checkpoint: English, or `multilingual` for German mail (uncalibrated, see the skill)
- [ ] Pin `JEV_MODEL` for the release
- [ ] Confirm the FSM (`governance.json` → `fsm.application`) matches the CRM's real stages

### 2. Build
- [ ] CRM calls `open_panel("job-crm")` once at startup and `panel.decide(state, questions, {"application": <current stage>})` once per email
- [ ] Sidecar as a service (systemd or Docker), health check at `/health`
- [ ] Apply `act` results. Queue `propose` (y/N buttons) and `review` (pick an answer). Store the human's answer as a label
- [ ] Surface the audit trail: `job-crm/logs/decisions.jsonl` (no text) and `llm_calls.jsonl` (tokens, cost)
- [ ] Feature flag around automatic `act`

### 3. Evaluate (before enabling the flag)
- [ ] Label 100-200 real emails (those already filed by hand count)
- [ ] Per question: accuracy of Laya, Jev and the panel; share of act / propose / review; p50/p95 latency; monthly cost
- [ ] Try 2-3 phrasings per question; tune thresholds and weights in `governance.json` from the data (bump its `version`)
- [ ] Go/no-go: `act` decisions ≥ 97% right, `review` share ≤ 25%, spend within the $5/month ceiling

### 4. Release
- [ ] Changelog and version bump
- [ ] Kill switch drill: `DECISION_REMOTE=0` stops all TypeSafe calls and shows up in every decision record
- [ ] Enable the flag for new mail only; watch the queues for a week
- [ ] Retro: keep, re-phrase, or fine-tune Laya on the collected labels

## Release notes (fill in)

| Question | Laya acc. | Jev acc. | Panel acc. | act / propose / review | p50 ms | Cost / month |
|---|---|---|---|---|---|---|
| stage | | | | | | |
| needs_reply | | | | | | |
| urgency | | | | | | |

## Risks

- **Personal data at TypeSafe.** Emails contain recruiters' and your personal data, and sending
  them is authorized (§3.1). Mitigations: per-question `"remote": false`, the kill switch,
  deleting `remote_authorization` to go fully local, and no message text in the logs.
- **Public repository.** `token8/test` is public. Code and config are fine there. Emails,
  `.env` and `logs/` are git-ignored and must stay so. If the CRM code has anything private
  in it, move `job-crm/` to a private repo.
- **Laya on non-English text.** The English checkpoint answers German mail confidently and
  wrongly. Use `multilingual` (or `laya.Router` with `lang=`), and re-check the thresholds.
- **Thresholds set by feel.** Blocked by step 3: the flag isn't flipped without measured numbers.
- **TypeSafe outage or price change.** The panel degrades to Laya alone with a higher bar
  (0.95), and the budget ceiling stops spend at $5/month.

## Change log

- 2026-09-25: Plan created (Laya first, Jev as fallback).
- 2026-09-25: Owner direction: call TypeSafe in parallel, and derive the final decision from
  governance and the manifesto. The decision panel, spec, `job-crm/` home and `.env`
  convention were added.
