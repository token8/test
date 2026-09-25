"""Question sets for the job-search CRM. Starting points: measure them on real mail before trusting them.

Questions ask what the text says (not what to do), and every option carries a description,
as the Laya skill recommends. Mapping answers to CRM actions happens in code.
"""

from .client import Policy


def job_email_questions():
    """Inbound email about an application: which pipeline stage it signals, and how urgent it is."""
    return {
        "stage": {
            "type": "choice",
            "instructions": "What does this email tell the candidate about their job application?",
            "criteria": {
                "received": "confirms an application was received or is under review",
                "interview": "invites to, schedules or moves an interview or assessment",
                "offer": "makes or discusses a job offer, salary or contract",
                "rejection": "declines the application or says the role is filled",
                "recruiter_outreach": "a recruiter introduces a new role the candidate has not applied for",
                "other": "newsletters, job alerts, receipts and anything else",
            },
        },
        "needs_reply": {"type": "noul", "instructions": "Does the sender ask the candidate to reply, confirm or choose a time?"},
        "urgency": {
            "type": "score",
            "instructions": "How soon does the candidate need to act on this email?",
            "criteria": ["no action needed", "within a week", "within a day or a stated deadline"],
        },
    }


# stage and needs_reply are clear-cut categories, where Laya is strongest; urgency is a `score`
# and goes to Jev by default (DecisionClient.always_remote).
JOB_EMAIL_POLICIES = {
    "stage": Policy(min_confidence=0.80),
    "needs_reply": Policy(min_confidence=0.90),
}


def job_fit_questions():
    """A job posting against the candidate's criteria (put the criteria in the state as words, not numbers)."""
    return {
        "fit": {
            "type": "score",
            "instructions": "How well does this job match the candidate's stated criteria?",
            "criteria": ["clear mismatch", "partial match", "strong match"],
        },
        "remote_ok": {"type": "noul", "instructions": "Does the posting allow fully remote work?"},
    }
