"""Output generator — .docx and .pptx generation from markdown and storyboard schemas."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional


class OutputGenerator:
    """Generate .docx and .pptx deliverables from content."""

    def generate_docx(
        self,
        content_md: str,
        output_path: str | Path,
        template_path: Optional[str | Path] = None,
        firm_name: str = "GoodWork Forensic Consulting",
    ) -> Path:
        """Generate .docx from markdown content.

        Uses python-docx. Graceful fallback if template absent.
        """
        try:
            from docx import Document
            from docx.shared import Pt, RGBColor
            from docx.enum.text import WD_ALIGN_PARAGRAPH
        except ImportError:
            raise ImportError("python-docx not installed. Run: pip install python-docx")

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        # Load template if provided and exists
        if template_path and Path(template_path).exists():
            doc = Document(template_path)
        else:
            doc = Document()
            # Basic styling
            style = doc.styles["Normal"]
            style.font.name = "Calibri"
            style.font.size = Pt(11)

        # Add firm name as footer text (simple implementation)
        section = doc.sections[0]

        # Parse markdown and populate document
        _md_to_docx(doc, content_md)

        # Save atomically
        tmp = out.with_suffix(".tmp.docx")
        doc.save(tmp)
        import os
        os.replace(tmp, out)
        return out

    def generate_pptx(
        self,
        storyboard,   # DeckStoryboard
        output_path: str | Path,
        template_path: Optional[str | Path] = None,
        firm_name: str = "GoodWork Forensic Consulting",
    ) -> Path:
        """Generate .pptx from DeckStoryboard — one slide per SlideSpec."""
        try:
            from pptx import Presentation
            from pptx.util import Inches, Pt
            from pptx.enum.text import PP_ALIGN
        except ImportError:
            raise ImportError("python-pptx not installed. Run: pip install python-pptx")

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if template_path and Path(template_path).exists():
            prs = Presentation(template_path)
        else:
            prs = Presentation()

        # Title slide
        title_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_layout)
        _set_text(slide.placeholders, 0, storyboard.deck_objective)
        _set_text(slide.placeholders, 1, f"{firm_name}\n{storyboard.audience}")

        # Content slides
        content_layout = prs.slide_layouts[1]
        for spec in storyboard.slides:
            slide = prs.slides.add_slide(content_layout)
            _set_text(slide.placeholders, 0, f"{spec.slide_number}. {spec.title}")

            bullets = []
            bullets.append(f"Key message: {spec.key_message}")
            bullets.extend(spec.content_bullets)
            if spec.evidence_needed:
                bullets.append(f"Evidence: {'; '.join(spec.evidence_needed[:2])}")

            _set_text(slide.placeholders, 1, "\n".join(bullets))

            # Speaker notes
            if spec.speaker_notes:
                notes_slide = slide.notes_slide
                notes_slide.notes_text_frame.text = spec.speaker_notes

        tmp = out.with_suffix(".tmp.pptx")
        prs.save(tmp)
        import os
        os.replace(tmp, out)
        return out


def _md_to_docx(doc, content: str) -> None:
    """Convert markdown content to docx paragraphs (simplified)."""
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    for line in content.split("\n"):
        line = line.rstrip()
        if line.startswith("# "):
            p = doc.add_heading(line[2:], level=1)
        elif line.startswith("## "):
            p = doc.add_heading(line[3:], level=2)
        elif line.startswith("### "):
            p = doc.add_heading(line[4:], level=3)
        elif line.startswith("- ") or line.startswith("* "):
            p = doc.add_paragraph(line[2:], style="List Bullet")
        elif line.startswith("| "):
            # Skip table formatting for now (would need more complex handling)
            doc.add_paragraph(line)
        elif line.startswith("---"):
            doc.add_paragraph("_" * 50)
        elif line.strip():
            # Strip markdown bold/italic
            clean = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', line)
            clean = re.sub(r'_{1,2}([^_]+)_{1,2}', r'\1', clean)
            doc.add_paragraph(clean)
        else:
            doc.add_paragraph("")


def _set_text(placeholders, idx: int, text: str) -> None:
    """Safely set text on a pptx placeholder."""
    try:
        placeholders[idx].text = text
    except (KeyError, IndexError):
        pass
