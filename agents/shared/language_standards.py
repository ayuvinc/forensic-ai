"""Language standard instruction blocks (P9-07B).

Injected into agent system prompts via build_system_prompt(language_standard=...).
One block per standard — appended verbatim after the agent's base prompt.
"""

from __future__ import annotations

LANGUAGE_STANDARD_BLOCKS: dict[str, str] = {
    "acfe": (
        "LANGUAGE STANDARD — ACFE INTERNAL REVIEW:\n"
        "Write in narrative style. Use qualified language for inferences "
        "('evidence suggests', 'it appears', 'the available evidence indicates'). "
        "Cite every source. Past tense. Third person. No pronouns."
    ),
    "expert_witness": (
        "LANGUAGE STANDARD — EXPERT WITNESS (COURT-READY):\n"
        "Write in court-ready format. Past tense only. Third person only. No pronouns. "
        "State only what is directly evidenced. No opinions or inferences — "
        "if inference is required, label it explicitly as a reasonable professional conclusion. "
        "Every assertion must be traceable to a documented procedure or exhibit."
    ),
    "regulatory": (
        "LANGUAGE STANDARD — REGULATORY SUBMISSION:\n"
        "Write in formal regulatory submission style. "
        "Cite regulations by full name and section number. "
        "Use prescribed structure for the relevant regulatory body. "
        "Past tense. Third person."
    ),
    "board_pack": (
        "LANGUAGE STANDARD — BOARD PACK:\n"
        "Write for a C-suite / board audience. Lead with business risk and impact. "
        "Minimise technical jargon. Past tense. Third person. "
        "Executive summary first, detail follows."
    ),
}


def get_language_block(standard: str) -> str:
    """Return the instruction block for the given standard. Defaults to 'acfe'."""
    return LANGUAGE_STANDARD_BLOCKS.get(standard, LANGUAGE_STANDARD_BLOCKS["acfe"])
