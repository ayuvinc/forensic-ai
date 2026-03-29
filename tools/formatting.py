"""Bilingual formatting — contextual Arabic translation with Gulf dialect nuances.

NOT literal MSA translation. Uses Claude to produce:
- Contextual, regionally nuanced Arabic
- Technical terms, entity names, regulation names stay in English
- Numeric values stay in English
- Gulf dialect where applicable
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Optional

from config import ANTHROPIC_API_KEY, HAIKU, TEMPLATES_DIR


def translate_to_arabic(
    content_en: str,
    document_type: str = "report",
    client_name: str = "",
    firm_name: str = "GoodWork Forensic Consulting",
) -> str:
    """Translate English content to Arabic — contextual, Gulf-nuanced.

    Preserves: regulation names, entity names, numeric values, English technical terms.
    """
    import anthropic

    glossary = _load_glossary()
    glossary_str = ""
    if glossary:
        glossary_str = f"\n\nSTANDARD GLOSSARY (use these translations):\n{glossary}"

    system = f"""You are a professional Arabic translator specialising in forensic, legal, and financial documents.

TRANSLATION RULES:
1. Use formal Modern Standard Arabic (MSA) appropriate for professional Gulf business context
2. Preserve in English (do NOT translate):
   - Regulation and law names (e.g. "CBUAE Notice No. 2", "FATF", "AML/CFT", "ISO 37001")
   - Entity names, company names, personal names
   - Financial figures and numeric values
   - Jurisdiction abbreviations (DFSA, ADGM, SCA, etc.)
   - Technical English acronyms (KYC, CDD, SAR, STR)
3. Use Gulf Arabic professional conventions — not Egyptian or Levantine dialect
4. Document type: {document_type}
5. Client: {client_name or 'Client'}
6. Firm: {firm_name}{glossary_str}

Translate the provided text. Return ONLY the Arabic translation, no English.
"""

    # Chunk large content
    chunks = _chunk_content(content_en, max_chars=6000)
    translated_chunks = []

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    for i, chunk in enumerate(chunks):
        resp = client.messages.create(
            model=HAIKU,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": f"Translate:\n\n{chunk}"}],
        )
        translated_chunks.append(resp.content[0].text.strip())

    return "\n\n".join(translated_chunks)


def _chunk_content(text: str, max_chars: int = 6000) -> list[str]:
    """Split content into chunks at paragraph boundaries."""
    if len(text) <= max_chars:
        return [text]

    paragraphs = text.split("\n\n")
    chunks = []
    current = []
    current_len = 0

    for para in paragraphs:
        if current_len + len(para) > max_chars and current:
            chunks.append("\n\n".join(current))
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += len(para)

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def _load_glossary() -> str:
    """Load Arabic glossary from templates/arabic_glossary.md."""
    glossary_path = TEMPLATES_DIR / "arabic_glossary.md"
    if glossary_path.exists():
        return glossary_path.read_text(encoding="utf-8")[:3000]
    return ""


def generate_bilingual_report(
    content_en: str,
    case_id: str,
    document_type: str = "report",
    client_name: str = "",
    firm_name: str = "GoodWork Forensic Consulting",
) -> tuple[str, str]:
    """Generate both EN and AR versions. Returns (content_en, content_ar)."""
    from tools.file_tools import write_final_report

    content_ar = translate_to_arabic(content_en, document_type, client_name, firm_name)
    write_final_report(case_id, content_ar, "ar")
    return content_en, content_ar
