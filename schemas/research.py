from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel


class Citation(BaseModel):
    # Empty string is valid — knowledge-only citations have no URL
    source_url: str = ""
    source_name: str
    source_type: Literal["authoritative", "news", "general", "unverified"]
    retrieved_at: datetime
    excerpt: str
    confidence: Literal["high", "medium", "low"]


class ResearchQuery(BaseModel):
    query: str
    tool: Literal["general_search", "regulatory_lookup", "sanctions_check", "company_lookup"]
    filters: Optional[dict] = None


class ResearchResult(BaseModel):
    query: str
    results: list[Citation]
    authoritative_citations: list[Citation]
    disclaimer: Optional[str] = None
