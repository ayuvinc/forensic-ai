"""Shared pytest fixtures for the forensic-ai test suite.

All fixtures use temporary directories — no production data is read or written.
All external API calls must be mocked — no ANTHROPIC_API_KEY or TAVILY_API_KEY required.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def tmp_cases_dir(tmp_path: Path) -> Path:
    """A temporary cases/ directory isolated per test."""
    cases = tmp_path / "cases"
    cases.mkdir()
    return cases


@pytest.fixture
def patched_cases_dir(tmp_cases_dir: Path, monkeypatch):
    """Monkeypatch tools.file_tools and config to use the temp cases dir.

    Ensures tests never touch the real cases/ directory.
    """
    import config
    import tools.file_tools as ft

    monkeypatch.setattr(config, "CASES_DIR", tmp_cases_dir)
    monkeypatch.setattr(ft, "CASES_DIR", tmp_cases_dir)
    monkeypatch.setattr(ft, "_INDEX_PATH", tmp_cases_dir / "index.json")
    return tmp_cases_dir


@pytest.fixture
def sample_case_id() -> str:
    return "20260419-TEST01"


@pytest.fixture
def mock_anthropic_client():
    """A mock Anthropic client that returns a stub text response."""
    client = MagicMock()
    message = MagicMock()
    message.content = [MagicMock(text="stub response")]
    message.stop_reason = "end_turn"
    client.messages.create.return_value = message
    return client


@pytest.fixture
def mock_config(monkeypatch):
    """Patch config constants used across tests — no real keys required."""
    import config
    monkeypatch.setattr(config, "ANTHROPIC_API_KEY", "sk-test-key")
    monkeypatch.setattr(config, "TAVILY_API_KEY", "")
    monkeypatch.setattr(config, "RESEARCH_MODE", "knowledge_only")
    return config
