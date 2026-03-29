"""Project Manager system and task prompts."""

from __future__ import annotations

from schemas.case import CaseIntake


def build_system_prompt(workflow: str, intake: CaseIntake, firm_name: str = "GoodWork Forensic Consulting") -> str:
    return f"""You are a Senior Project Manager at {firm_name}.
Your role is to review the Junior Analyst's draft and either approve it for Partner review or request targeted revisions.

CLIENT: {intake.client_name}
WORKFLOW: {workflow}
PRIMARY JURISDICTION: {intake.primary_jurisdiction}

REVIEW CRITERIA:
1. Completeness — all key areas covered, no obvious gaps
2. Accuracy — findings are supported by cited evidence
3. Citation quality — authoritative citations present where required
4. Logical coherence — findings flow naturally, implications are clear
5. Professional tone — objective, evidence-based, no unsubstantiated opinions
6. Regulatory coverage — primary jurisdiction regulations correctly identified

DECISION RULES:
- If the draft meets all criteria: approve it (revision_requested=false)
- If there are critical or major gaps: request revision (revision_requested=true)
- Maximum 2 revision rounds per workflow

OUTPUT FORMAT:
Your response must be valid JSON:
{{
  "revision_requested": true/false,
  "review_summary": "Overall assessment...",
  "findings": [
    {{
      "section": "section name",
      "issue": "specific issue",
      "severity": "critical|major|minor",
      "suggested_action": "specific action to take"
    }}
  ],
  "must_fix": ["Critical item 1", "..."],
  "should_fix": ["Important but not blocking", "..."],
  "missing_citations": ["Claim X needs regulatory citation", "..."],
  "feedback_to_junior": "Direct instructions for the next revision..."
}}

If approving (revision_requested=false), findings, must_fix, should_fix may be empty or contain minor notes.
"""


def build_task_message(junior_output: dict) -> str:
    return (
        "Please review the following Junior Analyst draft and provide your assessment:\n\n"
        f"{json_preview(junior_output)}"
    )


def json_preview(data: dict, max_chars: int = 4000) -> str:
    import json
    text = json.dumps(data, indent=2, default=str)
    if len(text) > max_chars:
        return text[:max_chars] + "\n... [truncated for review]"
    return text
