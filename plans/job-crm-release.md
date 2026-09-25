# Job search CRM: next release plan (decision layer)

> Status: **planning**. Started 2026-09-25. This file is the release checklist; tick items in
> the same PR that completes them, so the history shows who closed what and when.

## Goal

Ship a release where the CRM files and prioritises job-search mail and postings by itself,
using the [decision layer](../decision-layer/README.md): **Laya locally first, TypeSafe Jev as
fallback**. Nobody should have to sort a recruiter email by hand when the answer is obvious.
Anything uncertain lands in a review queue instead of being guessed.

## Scope

| Feature | Questions (`decision_layer/presets.py`) | Backend expectation |
|---|---|---|
| Auto-file inbound email to the application's stage (received / interview / offer / rejection / outreach) | `stage` (choice) | Laya; Jev below 0.80 |
| "Needs reply" flag on the dashboard | `needs_reply` (yes/no) | Laya; Jev below 0.90 |
| Urgency sort of the inbox | `urgency` (score) | Jev (Laya is weak on ordinal scores) |
| Fit score for saved job postings | `fit` (score), `remote_ok` (yes/no) | `fit` Jev, `remote_ok` Laya |
| Review queue for everything in `fallback_failed` | – | Human |

Out of scope for this release: generating replies, extracting salary or dates as values
(decision models do not generate text), and fine-tuning Laya (next release, if the numbers
call for it).

## Checklist

### 0. Setup (this repo)
- [x] Evaluate Laya and its benchmark against Jev (500 examples: Laya 67% / Jev 76% overall, level on simple questions, about 6× faster, free)
- [x] Reference implementation `decision-layer/`: Laya sidecar, Jev fallback, per-question policy, 9 unit tests
- [x] Laya integration skill vendored to `.claude/skills/laya-integration/` and house skill `.claude/skills/decision-layer/` added, so every project gets the paradigm
- [x] CRM question sets drafted (`presets.py`)
- [ ] **Link the CRM repository to this plan** (it is not in this repo; add it to the Claude session, or move this file there)
- [ ] Decide the release version number and target date

### 1. Decisions
- [ ] Privacy: which fields may go to TypeSafe. Suggested: `stage`/`needs_reply` stay local (`allow_remote=False`) if email bodies hold third-party personal data; send only posting text for `fit`
- [ ] TypeSafe account, API key stored as a secret (never in the repo), monthly spend cap
- [ ] Where the Laya sidecar runs (laptop, home server, VM with GPU/CPU), and the checkpoint: English or `multilingual` (for German-language mail; it is uncalibrated, see skill)
- [ ] Pin `JEV_MODEL` for the release

### 2. Build
- [ ] Vendor `decision_layer/` into the CRM (or port `decide()` to the CRM's language)
- [ ] Sidecar as a service (systemd/Docker), health check at `/health`, CRM degrades to "review queue" when both backends are down
- [ ] Email ingestion calls `decide()` once per email with all questions; state built with `laya.email_state()`-style cleanup (strip quotes and signatures)
- [ ] Map answers to CRM actions in code, behind a feature flag
- [ ] Review queue UI for `fallback_failed`; human corrections stored as labels for later evaluation
- [ ] Metrics without message text: source per question, escalation rate, p50/p95 latency, Jev input tokens

### 3. Evaluate (before enabling the flag)
- [ ] Label 100-200 real emails and 50 postings (the ones already filed by hand count)
- [ ] Accuracy per question for Laya, Jev and the combined client; escalation rate
- [ ] Try 2-3 phrasings per question, keep the best; set `min_confidence` from the data
- [ ] Record the numbers in the release notes below. Go/no-go: combined accuracy on `stage` ≥ 90%, and automatic actions at or above the threshold ≥ 97% right

### 4. Release
- [ ] Changelog and version bump
- [ ] Enable the flag for new mail only; watch escalation rate and review queue for a week
- [ ] Kill switch tested: `DECISION_REMOTE_FALLBACK=0` and flag off
- [ ] Retro: keep, re-phrase, or fine-tune Laya on the collected labels

## Release notes (fill in)

| Question | Laya acc. | Jev acc. | Combined | Escalation | p50 ms |
|---|---|---|---|---|---|
| stage | | | | | |
| needs_reply | | | | | |
| urgency | | | | | |
| fit | | | | | |

## Risks

- **Personal data in the fallback.** Mitigated by per-question `allow_remote` and the kill switch.
- **Laya answers non-English text confidently and wrongly on the English checkpoint.** Use `multilingual` (or `laya.Router` with `lang=`) for German mail, and re-check thresholds, as that checkpoint is uncalibrated.
- **Thresholds set by feel.** Blocked by step 3: no flag flip without measured numbers.
- **Vendor change at TypeSafe.** Fallback is optional by design; without a key the CRM still runs on Laya plus the review queue.
