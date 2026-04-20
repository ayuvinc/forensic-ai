"""ReviewAgent — post-pipeline AI review pass (P9-08).

Runs after Partner approval, before write_final_report().
Classifies each finding's evidence support level and rewrites text per language_standard.

Finding with citations=[] is classified 'unsupported' without a model call.
Results saved to D_Working_Papers/ai_review_{YYYYMMDD}.json.

Can be disabled by setting context["ai_review_enabled"] = False.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from schemas.artifacts import ReviewAnnotation

logger = logging.getLogger(__name__)

_SUPPORT_PROMPT = """You are reviewing a forensic finding for evidentiary support.

FINDING:
{finding_text}

CITATIONS PROVIDED:
{citations_text}

Classify this finding:
- "supported": citations directly substantiate the finding
- "partially_supported": citations partially support it; some claims lack evidence
- "unsupported": citations are absent or irrelevant to the claim

Then identify any logic_gaps (list of strings — specific logical or evidentiary gaps).

Finally, rewrite the finding text per the following language standard to improve precision:
{language_block}

Respond as JSON only:
{{
  "support_level": "supported|partially_supported|unsupported",
  "logic_gaps": ["gap 1", "gap 2"],
  "rewritten_text": "rewritten finding text"
}}"""


class ReviewAgent:
    """Post-pipeline review agent. Runs on each finding. Uses Haiku for speed/cost."""

    def __call__(
        self,
        draft: dict,
        context: dict,
    ) -> list[ReviewAnnotation]:
        """Review all findings in draft. Returns one ReviewAnnotation per finding.

        draft must have a "findings" key (list of dicts with at least "title" and
        optionally "citations" and "description"/"content").
        context may carry "language_standard" (defaults "acfe") and
        "ai_review_enabled" (defaults True).
        """
        if not context.get("ai_review_enabled", True):
            return []

        findings = draft.get("findings", [])
        if not findings:
            return []

        from agents.shared.language_standards import get_language_block
        language_standard = context.get("language_standard", "acfe")
        language_block = get_language_block(language_standard)

        annotations: list[ReviewAnnotation] = []
        for finding in findings:
            ann = self._review_finding(finding, language_block)
            annotations.append(ann)

        # Persist to D_Working_Papers/
        case_id = context.get("case_id", "")
        if case_id:
            self._persist(case_id, annotations, context)

        return annotations

    # ── Private ───────────────────────────────────────────────────────────────

    def _review_finding(self, finding: dict, language_block: str) -> ReviewAnnotation:
        finding_id = finding.get("title") or finding.get("risk_id") or finding.get("id", "unknown")
        citations = finding.get("citations", []) or finding.get("regulatory_references", [])

        # Auto-classify unsupported without model call when no citations
        if not citations:
            return ReviewAnnotation(
                finding_id=str(finding_id),
                support_level="unsupported",
                evidence_cited=[],
                logic_gaps=["No citations provided — claim cannot be independently verified."],
                rewritten_text=None,
            )

        finding_text = finding.get("description") or finding.get("content") or str(finding)
        citations_text = _format_citations(citations)

        try:
            result = self._call_model(finding_text, citations_text, language_block)
            return ReviewAnnotation(
                finding_id=str(finding_id),
                support_level=result.get("support_level", "partially_supported"),
                evidence_cited=[c if isinstance(c, str) else str(c) for c in citations[:5]],
                logic_gaps=result.get("logic_gaps", []),
                rewritten_text=result.get("rewritten_text"),
            )
        except Exception as exc:
            logger.warning("ReviewAgent: model call failed for finding %r: %s", finding_id, exc)
            return ReviewAnnotation(
                finding_id=str(finding_id),
                support_level="partially_supported",
                evidence_cited=[],
                logic_gaps=[f"Review skipped — model error: {exc}"],
                rewritten_text=None,
            )

    def _call_model(self, finding_text: str, citations_text: str, language_block: str) -> dict:
        import re
        import anthropic
        from config import ANTHROPIC_API_KEY, HAIKU

        prompt = _SUPPORT_PROMPT.format(
            finding_text=finding_text[:2000],
            citations_text=citations_text[:1000],
            language_block=language_block,
        )
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        resp = client.messages.create(
            model=HAIKU,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text

        # Parse JSON from response
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return json.loads(match.group())
        return {}

    def _persist(self, case_id: str, annotations: list[ReviewAnnotation], context: dict) -> None:
        """Write annotations to D_Working_Papers/ai_review_{YYYYMMDD}.json atomically."""
        try:
            from tools.file_tools import case_dir
            cdir = case_dir(case_id)
            working_papers = cdir / "D_Working_Papers"
            working_papers.mkdir(exist_ok=True)

            date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
            out_path = working_papers / f"ai_review_{date_str}.json"
            tmp_path = out_path.with_suffix(".tmp")

            payload = {
                "case_id": case_id,
                "workflow": context.get("workflow", ""),
                "language_standard": context.get("language_standard", "acfe"),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "annotations": [a.model_dump() for a in annotations],
            }
            import os
            tmp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            os.replace(tmp_path, out_path)
        except Exception as exc:
            logger.warning("ReviewAgent: persist failed: %s", exc)


def _format_citations(citations: list) -> str:
    parts = []
    for c in citations[:5]:
        if isinstance(c, dict):
            parts.append(c.get("source_name") or c.get("source_url") or str(c))
        elif hasattr(c, "source_name"):
            parts.append(c.source_name)
        else:
            parts.append(str(c))
    return "; ".join(parts) if parts else "None"
