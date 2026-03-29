"""Email parser — .eml (email.message + html2text) and .msg (extract-msg + html2text).

Parent-child attachment linking. Haiku entity extraction.
"""

from __future__ import annotations

import email
import email.policy
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ParsedEmail:
    filepath: str
    from_addr: str = ""
    to_addr: str = ""
    cc_addr: str = ""
    subject: str = ""
    date: str = ""
    body_text: str = ""
    attachments: list[str] = field(default_factory=list)   # filenames of attachments
    attachment_paths: list[str] = field(default_factory=list)  # saved paths
    headers: dict = field(default_factory=dict)
    message_id: str = ""


def parse_eml(filepath: str | Path) -> ParsedEmail:
    """Parse .eml file using stdlib email module + html2text for HTML bodies."""
    fpath = Path(filepath)
    raw = fpath.read_bytes()

    try:
        msg = email.message_from_bytes(raw, policy=email.policy.default)
    except Exception:
        msg = email.message_from_bytes(raw)

    result = ParsedEmail(filepath=str(fpath))
    result.from_addr     = str(msg.get("From", ""))
    result.to_addr       = str(msg.get("To", ""))
    result.cc_addr       = str(msg.get("Cc", ""))
    result.subject       = str(msg.get("Subject", ""))
    result.date          = str(msg.get("Date", ""))
    result.message_id    = str(msg.get("Message-ID", ""))
    result.headers       = dict(msg.items())

    body_parts = []
    for part in msg.walk():
        ct = part.get_content_type()
        cd = str(part.get("Content-Disposition", ""))

        if "attachment" in cd:
            filename = part.get_filename()
            if filename:
                result.attachments.append(filename)
            continue

        if ct == "text/plain":
            payload = part.get_payload(decode=True)
            if payload:
                body_parts.append(payload.decode("utf-8", errors="replace"))

        elif ct == "text/html":
            payload = part.get_payload(decode=True)
            if payload:
                html_text = payload.decode("utf-8", errors="replace")
                body_parts.append(_html_to_text(html_text))

    result.body_text = "\n\n".join(body_parts)
    return result


def parse_msg(filepath: str | Path) -> ParsedEmail:
    """Parse .msg (Outlook) file using extract-msg library."""
    try:
        import extract_msg
    except ImportError:
        raise ImportError("extract-msg not installed. Run: pip install extract-msg")

    fpath = Path(filepath)
    try:
        msg = extract_msg.Message(fpath)
    except Exception as e:
        raise ValueError(f"Could not parse .msg file: {e}")

    result = ParsedEmail(filepath=str(fpath))
    result.from_addr  = str(msg.sender or "")
    result.to_addr    = str(msg.to or "")
    result.cc_addr    = str(msg.cc or "")
    result.subject    = str(msg.subject or "")
    result.date       = str(msg.date or "")
    result.message_id = str(msg.messageId or "")

    body = msg.body or ""
    if msg.htmlBody:
        html = msg.htmlBody
        if isinstance(html, bytes):
            html = html.decode("utf-8", errors="replace")
        body = _html_to_text(html)

    result.body_text = body

    # Extract attachment names
    for att in (msg.attachments or []):
        name = getattr(att, "longFilename", None) or getattr(att, "shortFilename", None)
        if name:
            result.attachments.append(name)

    return result


def parse_email_file(filepath: str | Path) -> ParsedEmail:
    """Auto-detect .eml vs .msg and parse accordingly."""
    fpath = Path(filepath)
    if fpath.suffix.lower() == ".msg":
        return parse_msg(fpath)
    return parse_eml(fpath)


def to_text_representation(parsed: ParsedEmail) -> str:
    """Convert ParsedEmail to plain-text for agent consumption."""
    lines = [
        f"From: {parsed.from_addr}",
        f"To: {parsed.to_addr}",
        f"Cc: {parsed.cc_addr}" if parsed.cc_addr else "",
        f"Subject: {parsed.subject}",
        f"Date: {parsed.date}",
        f"Message-ID: {parsed.message_id}",
        "",
    ]
    if parsed.attachments:
        lines.append(f"Attachments: {', '.join(parsed.attachments)}")
        lines.append("")
    lines.append(parsed.body_text)
    return "\n".join(l for l in lines if l is not None)


def _html_to_text(html: str) -> str:
    """Convert HTML to plain text using html2text if available, fallback to regex."""
    try:
        import html2text
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.body_width = 0
        return h.handle(html)
    except ImportError:
        # Fallback: strip tags
        text = re.sub(r'<[^>]+>', ' ', html)
        return re.sub(r'\s+', ' ', text).strip()
