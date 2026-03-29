"""Partner agent tool definitions and registry setup."""

from __future__ import annotations

from core.tool_registry import ToolRegistry
from tools.research.regulatory_lookup import RegulatoryLookup


def get_tool_definitions() -> list[dict]:
    return [
        {
            "name": "regulatory_lookup",
            "description": "Verify regulatory requirements from authoritative sources before approving.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Regulatory query"},
                    "jurisdictions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Jurisdictions to search. Defaults to ['UAE'].",
                    },
                    "max_results": {"type": "integer", "default": 5},
                },
                "required": ["query"],
            },
        },
        {
            "name": "read_excerpt",
            "description": "Read the first N characters of a case document for reference.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "Document ID"},
                    "max_chars": {"type": "integer", "default": 8000},
                },
                "required": ["doc_id"],
            },
        },
        {
            "name": "read_section",
            "description": "Read a specific section of a large document.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "Document ID"},
                    "section_id": {"type": "string", "description": "Section ID"},
                },
                "required": ["doc_id", "section_id"],
            },
        },
    ]


def register_tools(registry: ToolRegistry, document_manager=None) -> None:
    """Register Partner tools."""
    if "regulatory_lookup" not in registry.list_tools():
        reg = RegulatoryLookup()
        registry.register("regulatory_lookup", reg.search)

    if document_manager:
        if "read_excerpt" not in registry.list_tools():
            registry.register("read_excerpt", document_manager.read_excerpt)
        if "read_section" not in registry.list_tools():
            registry.register("read_section", document_manager.read_section)
