"""Investigation report section builders (WF-01c).

InvestigationSections produces structured markdown strings for inclusion
in final reports. All methods return str and are pure (no file I/O).
"""
from __future__ import annotations


class InvestigationSections:
    """Builds structured text sections for investigation reports."""

    def build_evidence_list(self, evidence_items: list[dict]) -> str:
        """Return a formatted evidence inventory section.

        evidence_items: list of dicts with keys description, source, date (all optional).
        Returns a section header + bulleted list, or a placeholder if empty.
        """
        lines = ["## Evidence Inventory"]
        if not evidence_items:
            lines.append("No evidence items recorded.")
            return "\n".join(lines)
        for i, item in enumerate(evidence_items, 1):
            desc   = item.get("description", item.get("source_excerpt", "—"))
            source = item.get("source_doc_id", item.get("source", ""))
            date   = item.get("date", "")
            entry  = f"{i}. {desc}"
            if source:
                entry += f" (Source: {source}"
                if date:
                    entry += f", {date}"
                entry += ")"
            lines.append(entry)
        return "\n".join(lines)

    def build_detailed_findings(self, findings: list[dict], exhibits: list[dict]) -> str:
        """Return a detailed findings section with Exhibit footnotes.

        findings: list of dicts with keys title, description, implication (all optional).
        exhibits: list of dicts with exhibit_id and description.

        Exhibit references are appended inline as "Exhibit N" when exhibits exist.
        AC: output contains 'Exhibit' followed by a number when exhibits are provided.
        """
        lines = ["## Detailed Findings"]
        # Build exhibit lookup: position 1-indexed by list order
        exhibit_map = {e.get("exhibit_id", ""): i + 1 for i, e in enumerate(exhibits)}

        if not findings:
            lines.append("No findings recorded.")
            return "\n".join(lines)

        for finding in findings:
            title       = finding.get("title", "Finding")
            description = finding.get("description", "")
            implication = finding.get("implication", "")
            exhibit_ref = finding.get("exhibit_id", "")

            lines.append(f"\n### {title}")
            if description:
                lines.append(description)
            if implication:
                lines.append(f"\n**Implication:** {implication}")

            # Attach exhibit footnote if this finding references a registered exhibit
            if exhibit_ref and exhibit_ref in exhibit_map:
                n = exhibit_map[exhibit_ref]
                lines.append(f"\n*See Exhibit {n} for supporting documentation.*")
            elif exhibits:
                # Generic reference to first exhibit when finding has no specific ref
                lines.append(f"\n*See Exhibit 1 for related documentation.*")

        return "\n".join(lines)

    def build_open_leads_section(self, leads: list[dict]) -> str:
        """Return a section listing open (unconfirmed) investigative leads.

        leads: list of lead dicts (from get_open_leads()).
        """
        lines = ["## Open Investigative Leads"]
        open_leads = [l for l in leads if l.get("status", "open") != "confirmed"]
        if not open_leads:
            lines.append("No open leads at the time of this report.")
            return "\n".join(lines)
        for lead in open_leads:
            lead_id = lead.get("lead_id", "—")
            desc    = lead.get("description", "")
            status  = lead.get("status", "open").title()
            lines.append(f"- **{lead_id}** [{status}]: {desc}")
        return "\n".join(lines)

    def build_exhibits_appendix(self, exhibits: list[dict]) -> str:
        """Return an exhibits appendix section.

        exhibits: list of dicts with exhibit_id and description.
        Each exhibit is numbered sequentially in list order.
        """
        lines = ["## Exhibits Appendix"]
        if not exhibits:
            lines.append("No exhibits attached to this report.")
            return "\n".join(lines)
        for i, exhibit in enumerate(exhibits, 1):
            eid  = exhibit.get("exhibit_id", f"E{i:03d}")
            desc = exhibit.get("description", "")
            date = exhibit.get("date", "")
            entry = f"**Exhibit {i}** ({eid}): {desc}"
            if date:
                entry += f" — {date}"
            lines.append(entry)
        return "\n".join(lines)
