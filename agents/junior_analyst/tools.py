"""Junior Analyst tool definitions and registry setup."""

from __future__ import annotations

from core.tool_registry import ToolRegistry
from tools.research.general_search import GeneralSearch
from tools.research.regulatory_lookup import RegulatoryLookup
from tools.research.sanctions_check import SanctionsCheck
from tools.research.company_lookup import CompanyLookup


_DOC_TOOL_NAMES = {"read_excerpt", "read_pages", "read_section", "find_relevant_docs"}


def get_tool_definitions(document_manager=None) -> list[dict]:
    """Return Anthropic tool definitions for Junior Analyst's allowed tools.

    Document tools are only included when a document_manager is provided —
    if not registered they cannot be called and should not be offered to the model.
    """
    all_tools = [
        {
            "name": "search_web",
            "description": "Search the web for general information using Tavily. Returns citations with low-trust flag.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "description": "Max results to return", "default": 5},
                },
                "required": ["query"],
            },
        },
        {
            "name": "regulatory_lookup",
            "description": (
                "Search authoritative regulatory sources for given jurisdictions. "
                "ONLY use this for verified regulatory requirements. "
                "If no authoritative source found, returns explicit disclaimer."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Regulatory query"},
                    "jurisdictions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Jurisdictions to search (e.g. ['UAE', 'Saudi Arabia']). Defaults to ['UAE'].",
                    },
                    "max_results": {"type": "integer", "default": 5},
                },
                "required": ["query"],
            },
        },
        {
            "name": "sanctions_check",
            "description": "Check entity against OFAC SDN, UN, and EU sanctions lists. Authoritative only.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "entity_name": {"type": "string", "description": "Name of entity to check"},
                },
                "required": ["entity_name"],
            },
        },
        {
            "name": "company_lookup",
            "description": "Look up company registration and ownership in official registries.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string", "description": "Company name to look up"},
                    "jurisdictions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Jurisdictions to search. Defaults to ['UAE'].",
                    },
                },
                "required": ["company_name"],
            },
        },
        {
            "name": "read_excerpt",
            "description": (
                "Read the first N characters of a case document. "
                "Always start here — NEVER try to read a full document. "
                "Returns navigation hints for large documents."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "Document ID from the document index"},
                    "max_chars": {"type": "integer", "description": "Maximum characters to return", "default": 8000},
                },
                "required": ["doc_id"],
            },
        },
        {
            "name": "read_pages",
            "description": "Read specific pages of a case document. Use after read_excerpt to navigate large docs.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "Document ID"},
                    "page_range": {"type": "string", "description": "Page range, e.g. '5' or '12-18'"},
                },
                "required": ["doc_id", "page_range"],
            },
        },
        {
            "name": "read_section",
            "description": "Read a named section of a large document by section_id.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "Document ID"},
                    "section_id": {"type": "string", "description": "Section ID from the document index"},
                },
                "required": ["doc_id", "section_id"],
            },
        },
        {
            "name": "find_relevant_docs",
            "description": "Find documents in the case folder relevant to a query. Returns matching document entries.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search terms"},
                },
                "required": ["query"],
            },
        },
    ]
    if document_manager is None:
        return [t for t in all_tools if t["name"] not in _DOC_TOOL_NAMES]
    return all_tools


def register_tools(registry: ToolRegistry, document_manager=None) -> None:
    """Register Junior Analyst tools into the global registry."""
    search = GeneralSearch()
    reg    = RegulatoryLookup()
    sanc   = SanctionsCheck()
    comp   = CompanyLookup()

    registry.register("search_web",        search.search)
    registry.register("regulatory_lookup", reg.search)
    registry.register("sanctions_check",   sanc.check)
    registry.register("company_lookup",    comp.lookup)

    if document_manager:
        registry.register("read_excerpt",      document_manager.read_excerpt)
        registry.register("read_pages",        document_manager.read_pages)
        registry.register("read_section",      document_manager.read_section)
        registry.register("find_relevant_docs", document_manager.find_relevant_docs)
