"""Project Manager tool definitions and registry setup."""

from __future__ import annotations

from core.tool_registry import ToolRegistry


_DOC_TOOL_NAMES = {"read_excerpt", "read_section"}


def get_tool_definitions(document_manager=None) -> list[dict]:
    """Return Anthropic tool definitions for PM's allowed tools.

    Document tools are only included when a document_manager is provided.
    """
    all_tools = [
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
            "description": "Read a specific section of a large document by section_id.",
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
    if document_manager is None:
        return [t for t in all_tools if t["name"] not in _DOC_TOOL_NAMES]
    return all_tools


def register_tools(registry: ToolRegistry, document_manager=None) -> None:
    """Register PM tools. Doc tools only if document_manager provided and not already registered."""
    if document_manager:
        if "read_excerpt" not in registry.list_tools():
            registry.register("read_excerpt", document_manager.read_excerpt)
        if "read_section" not in registry.list_tools():
            registry.register("read_section", document_manager.read_section)
