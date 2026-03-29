"""Sanctions check — authoritative sources only.

Allowed domains: ofac.treas.gov, un.org, sanctions.ec.europa.eu
If no match found: returns explicit "no authoritative match identified".
NEVER infers a sanctions match. NEVER uses general web results.
"""

from datetime import datetime, timezone

from tavily import TavilyClient

from config import TAVILY_API_KEY
from schemas.research import Citation, ResearchResult

SANCTIONS_DOMAINS = [
    "ofac.treas.gov",
    "un.org",
    "sanctions.ec.europa.eu",
]

NO_MATCH_DISCLAIMER = (
    "No authoritative sanctions match identified from OFAC, UN, or EU sources. "
    "This is not a clearance — conduct independent verification before relying on this result."
)


class SanctionsCheck:
    def __init__(self):
        self._client = None

    def _get_client(self) -> TavilyClient:
        if self._client is None:
            self._client = TavilyClient(api_key=TAVILY_API_KEY)
        return self._client

    def check(self, entity_name: str, max_results: int = 5) -> ResearchResult:
        query = f"{entity_name} sanctions designation"
        raw = self._get_client().search(
            query=query,
            max_results=max_results,
            include_domains=SANCTIONS_DOMAINS,
        )

        authoritative = []
        for r in raw.get("results", []):
            url = r.get("url", "")
            if any(domain in url for domain in SANCTIONS_DOMAINS):
                authoritative.append(Citation(
                    source_url=url,
                    source_name=r.get("title", url),
                    source_type="authoritative",
                    retrieved_at=datetime.now(timezone.utc),
                    excerpt=r.get("content", "")[:2000],
                    confidence="high",
                ))

        if not authoritative:
            return ResearchResult(
                query=query,
                results=[],
                authoritative_citations=[],
                disclaimer=NO_MATCH_DISCLAIMER,
            )

        return ResearchResult(
            query=query,
            results=authoritative,
            authoritative_citations=authoritative,
            disclaimer="Match found in authoritative sanctions list — verify before acting.",
        )
