# Job search CRM

Home of the job search CRM. The release plan and checklist are in
[`plans/job-crm-release.md`](../plans/job-crm-release.md).

## Layout

```
job-crm/
  decisions/
    questions.json     typed questions for Laya and Jev (any language can read it)
    governance.json    how votes become act / propose / review; inherits the manifesto (v3.1)
    eval/sample.jsonl  label format, with fictional examples (real labels go in data/)
  .env.example         copy to .env (git-ignored) and add TYPESAFE_API_KEY
  .gitignore           keeps .env, logs/ and data/ out of git
  logs/                decisions.jsonl and llm_calls.jsonl (created at runtime, git-ignored)
  data/                real labelled emails and eval reports (git-ignored)
  src/                 ← the CRM code goes here (core/ business logic, infrastructure/ vendors: §10)
```

## Where the code goes

Check the CRM into `job-crm/src/`, with business logic and vendor code kept apart (§10 Clean
Core). **This repository is public**: never commit emails, contacts, exports or `.env`. If
anything in the code itself is private, move `job-crm/` to a private repository and this
folder moves with it unchanged.

## Using decisions from the CRM

```bash
docker compose -f decision-layer/docker/compose.yaml up -d  # Laya on 127.0.0.1:8771
cp job-crm/.env.example job-crm/.env                        # add TYPESAFE_API_KEY
```

```python
import sys; sys.path.insert(0, "decision-layer")           # or vendor decision_layer/
from decision_layer.infrastructure import open_panel, load_questions

panel, questions = open_panel("job-crm"), load_questions("job-crm")
d = panel.decide({"subject": subject, "body": body}, questions, {"application": app.stage})

for qid, r in d.results.items():
    if r["status"] == "act":       apply(qid, r["value"], r["transition"])
    elif r["status"] == "propose": approval_queue.add(qid, r)      # human y/N
    else:                          review_queue.add(qid, r)        # human decides
```

For a CRM that isn't written in Python, run the panel as a small service, or port
`decision_layer/core/` (about 200 lines). The JSON files and the rules stay the same.
