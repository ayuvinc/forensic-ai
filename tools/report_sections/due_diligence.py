"""Due Diligence report section builders (WF-02).

DDSections supports per-subject and consolidated report formats.
All methods return str and are pure (no file I/O).

AC: subjects=[] returns a non-empty section header string — no crash.
"""
from __future__ import annotations


class DDSections:
    """Builds structured text sections for Due Diligence reports."""

    def build_per_subject_section(self, subjects: list[dict]) -> str:
        """Return a per-subject findings section.

        subjects: list of dicts with keys name, subject_type, findings (list[str]),
                  risk_level, adverse_media (list[str]), sanctions_hits (list[str]).
        """
        lines = ["## Subject Due Diligence Findings"]
        if not subjects:
            lines.append("No subjects recorded for this engagement.")
            return "\n".join(lines)

        for i, subject in enumerate(subjects, 1):
            name         = subject.get("name", f"Subject {i}")
            stype        = subject.get("subject_type", "individual").title()
            risk_level   = subject.get("risk_level", "pending").upper()
            findings     = subject.get("findings", [])
            adverse      = subject.get("adverse_media", [])
            sanctions    = subject.get("sanctions_hits", [])

            lines.append(f"\n### {i}. {name} ({stype})")
            lines.append(f"**Risk Level:** {risk_level}")

            if findings:
                lines.append("\n**Key Findings:**")
                for f in findings:
                    lines.append(f"- {f}")

            if adverse:
                lines.append("\n**Adverse Media:**")
                for a in adverse:
                    lines.append(f"- {a}")

            if sanctions:
                lines.append("\n**Sanctions Hits:**")
                for s in sanctions:
                    lines.append(f"- {s}")

            if not findings and not adverse and not sanctions:
                lines.append("No derogatory information identified at this stage.")

        return "\n".join(lines)

    def build_consolidated_section(self, subjects: list[dict]) -> str:
        """Return a consolidated multi-subject summary section.

        subjects: same schema as build_per_subject_section.
        Produces an aggregate risk matrix table (markdown) across all subjects.
        """
        lines = ["## Consolidated Due Diligence Summary"]
        if not subjects:
            lines.append("No subjects recorded for this engagement.")
            return "\n".join(lines)

        # Summary table
        lines.append("\n| # | Subject | Type | Risk Level | Adverse Media | Sanctions |")
        lines.append("|---|---------|------|------------|---------------|-----------|")
        for i, subject in enumerate(subjects, 1):
            name       = subject.get("name", f"Subject {i}")
            stype      = subject.get("subject_type", "individual").title()
            risk_level = subject.get("risk_level", "pending").upper()
            adverse    = "Yes" if subject.get("adverse_media") else "None identified"
            sanctions  = "Yes" if subject.get("sanctions_hits") else "None identified"
            lines.append(f"| {i} | {name} | {stype} | {risk_level} | {adverse} | {sanctions} |")

        # Overall risk narrative
        high_risk = [s.get("name", "") for s in subjects if s.get("risk_level", "").lower() == "high"]
        if high_risk:
            lines.append(f"\n**High-risk subjects:** {', '.join(high_risk)}")
        else:
            lines.append("\nNo subjects assessed at high risk at this stage.")

        return "\n".join(lines)
