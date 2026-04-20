"""Document management schemas — provenance, index, timeline, interviews, Excel analysis."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel


class PermissibilityStatus(str, Enum):
    PERMISSIBLE  = "permissible"
    LEAD_ONLY    = "lead_only"
    INADMISSIBLE = "inadmissible"


# Literal alias kept for backward-compatible field annotations
PermissibilityLiteral = Literal["permissible", "lead_only", "inadmissible"]


class DocumentProvenance(BaseModel):
    """Chain-of-custody and authority basis for a document or evidence item."""
    collection_method: str        # "uploaded_by_consultant" | "system_extract" | "interview" | "subpoena"
    collected_at: datetime
    collector_role: str           # "consultant" | "client_representative" | "third_party"
    scope_authorized_by: str      # reference to engagement letter section or verbal authorization
    source_hash: str              # SHA-256 of original file — deduplication + integrity
    derived_from: Optional[str] = None  # doc_id of parent if this is an attachment or extract
    chain_of_custody_notes: str = ""


class DocumentSection(BaseModel):
    section_id: str
    section_title: str
    page_range: Optional[str] = None      # e.g. "12-18"
    char_start: Optional[int] = None      # character offset in extracted text
    char_end: Optional[int] = None
    summary: str                          # 2-3 sentence model-generated summary
    key_entities: list[str] = []
    flagged: bool = False


class DocumentEntry(BaseModel):
    doc_id: str
    case_id: str
    filename: str
    filepath: str                         # relative to case dir — pathlib-safe
    folder: str
    doc_type: Literal[
        "engagement_letter", "interview_transcript", "financial_records",
        "correspondence", "corporate_filing", "policy_sop",
        "previous_report", "excel_data", "email", "attachment", "other"
    ]
    size_bytes: int
    char_count: Optional[int] = None      # populated after text extraction
    page_count: Optional[int] = None
    is_large: bool = False                # True if char_count > SMALL_DOC_THRESHOLD
    summary: Optional[str] = None        # model-generated for small docs
    sections: list[DocumentSection] = [] # populated for large docs
    provenance: DocumentProvenance
    permissibility: PermissibilityLiteral = "permissible"
    attachments: list[str] = []          # doc_ids of child attachments
    indexed_at: datetime
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None  # doc_id of original
    embedding_status: Literal["indexed", "pending", "failed", "unavailable"] = "unavailable"
    chunk_count: Optional[int] = None      # populated after embedding; None if not embedded


class DocumentIndex(BaseModel):
    case_id: str
    documents: list[DocumentEntry] = []
    last_updated: datetime
    engagement_letter_doc_id: Optional[str] = None
    proposed_folder_structure: Optional[dict] = None
    folder_confirmed: bool = False


class TimelineEvent(BaseModel):
    event_id: str
    date: Optional[str] = None           # ISO or approximate
    date_confidence: Literal["exact", "approximate", "inferred"]
    description: str
    source_doc_id: str
    source_excerpt: str                   # verbatim excerpt — for citation
    parties_involved: list[str] = []
    event_type: Literal[
        "transaction", "communication", "contract",
        "meeting", "regulatory_event", "personnel_change", "other"
    ]
    permissibility: PermissibilityLiteral = "permissible"


class CaseTimeline(BaseModel):
    case_id: str
    events: list[TimelineEvent] = []     # sorted by date
    last_updated: datetime


class InterviewRecord(BaseModel):
    interview_id: str
    interviewee_name: str
    interviewee_role: str
    interview_date: Optional[str] = None
    key_statements: list[str] = []
    potential_admissions: list[str] = []
    contradictions: list[str] = []       # contradictions with other evidence
    source_doc_id: str
    provenance: DocumentProvenance


class ExcelAnomaly(BaseModel):
    anomaly_type: Literal[
        "duplicate_payment", "round_number", "split_transaction",
        "vendor_concentration", "outlier_amount", "timing_pattern",
        "missing_sequence", "journal_override", "other"
    ]
    description: str
    sheet: str
    rows_affected: list[int] = []
    risk_rating: Literal["high", "medium", "low"]
    recommended_procedure: str


class ExcelAnalysisResult(BaseModel):
    doc_id: str
    filename: str
    sheet_names: list[str] = []
    total_rows: int
    anomalies: list[ExcelAnomaly] = []
    methodology: str
