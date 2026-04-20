"""Sanctions report section builders (WF-04).

SanctionsSections builds structured markdown for sanctions screening reports.
Valid dispositions enforce a controlled vocabulary — build_hit_detail raises
ValueError on an unrecognised disposition value.
"""
from __future__ import annotations

VALID_DISPOSITIONS = frozenset({
    "True Match",
    "False Positive",
    "Requires Investigation",
    "Escalate",
})


class SanctionsSections:
    """Builds structured text sections for sanctions screening reports."""

    def build_hit_detail(self, hit: dict, disposition: str) -> str:
        """Return a detailed markdown block for a single sanctions hit.

        disposition must be one of: True Match / False Positive /
        Requires Investigation / Escalate.

        Raises ValueError for any unrecognised disposition value — callers
        must validate before calling to avoid silent mislabelling.
        """
        if disposition not in VALID_DISPOSITIONS:
            raise ValueError(
                f"Invalid disposition '{disposition}'. "
                f"Must be one of: {', '.join(sorted(VALID_DISPOSITIONS))}"
            )

        subject_name = hit.get("subject_name", "—")
        list_name    = hit.get("list_name", "—")
        match_score  = hit.get("match_score", "—")
        rationale    = hit.get("rationale", "")
        listed_date  = hit.get("listed_date", "—")

        disposition_prefix = {
            "True Match":             "CONFIRMED HIT",
            "False Positive":         "FALSE POSITIVE",
            "Requires Investigation": "UNDER REVIEW",
            "Escalate":               "ESCALATED",
        }[disposition]

        lines = [
            f"### [{disposition_prefix}] {subject_name}",
            f"**List:** {list_name}  |  **Match Score:** {match_score}  |  "
            f"**Listed:** {listed_date}",
            f"**Disposition:** {disposition}",
        ]
        if rationale:
            lines.append(f"\n**Rationale:** {rationale}")

        return "\n".join(lines)

    def build_false_positive_table(self, hits: list[dict]) -> str:
        """Return a markdown table of hits classified as False Positive.

        hits: full hit list — this method filters for False Positive entries.
        """
        lines = ["## False Positive Log"]
        fps = [h for h in hits if h.get("disposition", "") == "False Positive"]
        if not fps:
            lines.append("No false positives identified in this screening run.")
            return "\n".join(lines)

        lines.append("\n| # | Subject Name | List | Match Score | Reason |")
        lines.append("|---|-------------|------|-------------|--------|")
        for i, h in enumerate(fps, 1):
            name   = h.get("subject_name", "—")
            lst    = h.get("list_name", "—")
            score  = h.get("match_score", "—")
            reason = h.get("false_positive_reason", h.get("rationale", "—"))
            lines.append(f"| {i} | {name} | {lst} | {score} | {reason} |")

        return "\n".join(lines)

    def build_exec_summary(self, results: dict, policy: dict) -> str:
        """Return an executive summary section.

        results: dict with keys total_subjects, confirmed_hits, false_positives,
                 under_review, escalated.
        policy: sanctions_disposition_policy dict (from firm_profile/).
        """
        lines = ["## Sanctions Screening — Executive Summary"]

        total      = results.get("total_subjects", 0)
        confirmed  = results.get("confirmed_hits", 0)
        fps        = results.get("false_positives", 0)
        review     = results.get("under_review", 0)
        escalated  = results.get("escalated", 0)
        default_d  = policy.get("default_disposition", "Requires Investigation")

        lines.append(f"\n**Subjects screened:** {total}")
        lines.append(f"**Confirmed hits:** {confirmed}")
        lines.append(f"**False positives:** {fps}")
        lines.append(f"**Under review:** {review}")
        lines.append(f"**Escalated:** {escalated}")
        lines.append(f"\n**Firm default disposition:** {default_d}")

        if confirmed > 0:
            lines.append(
                f"\n**ALERT:** {confirmed} confirmed hit(s) identified. "
                "Engagement should not proceed without compliance sign-off."
            )
        elif escalated > 0:
            lines.append(
                f"\n{escalated} hit(s) escalated for senior review before clearance."
            )
        else:
            lines.append("\nNo confirmed hits. Engagement may proceed subject to standard KYC.")

        return "\n".join(lines)
