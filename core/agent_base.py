"""BaseAgent — agentic loop with tool dispatch, guardrails, and hook integration.

Every agent (Junior, PM, Partner) subclasses BaseAgent and provides:
  - system_prompt: str
  - tool_definitions: list[dict]  (Anthropic tool format)

The agentic loop runs until:
  - stop_reason == "end_turn"
  - max_turns is reached (raises MaxTurnsError)
  - timeout_seconds elapsed (raises AgentTimeoutError)
  - A tool call is not in the manifest's required_tools (raises ToolNotAllowedError)
"""

import re
import time
from dataclasses import dataclass, field
from typing import Any

import anthropic

from config import (
    ANTHROPIC_API_KEY,
    MAX_API_RETRIES,
    MAX_RESEARCH_EXCERPT_CHARS,
    RESEARCH_MODE,
    RETRY_BACKOFF_SECONDS,
    get_model,
)
from core.hook_engine import HookEngine
from core.tool_registry import ToolRegistry, ToolNotAllowedError


# ── Manifest (lightweight — full PluginManifest lives in schemas/plugins.py) ──

@dataclass
class AgentManifest:
    plugin_id: str
    model_preference: str          # "haiku" | "sonnet" | "opus"
    max_turns: int
    timeout_seconds: int
    required_tools: list[str]
    revision_capable: bool = False
    supported_workflows: list[str] = field(default_factory=list)
    max_tokens: int = 8192


# ── Errors ────────────────────────────────────────────────────────────────────

class MaxTurnsError(Exception):
    pass

class AgentTimeoutError(Exception):
    pass

class NoCitationsError(Exception):
    """Raised when a workflow requires citations but the agent produced none."""
    pass


# ── Prompt-injection guard ────────────────────────────────────────────────────

_HTML_TAG   = re.compile(r'<[^>]+>', re.IGNORECASE)
_SCRIPT_TAG = re.compile(r'<script.*?</script>', re.IGNORECASE | re.DOTALL)

# Web tools produce untrusted content — truncate after HTML strip.
# Document tools manage their own ceiling via DOC_SECTION_MAX_CHARS — do NOT truncate here
# or bounded retrieval (read_excerpt → 8k, read_pages → 60k) is silently nullified.
_WEB_TOOLS = frozenset({
    "search_web", "regulatory_lookup", "sanctions_check", "company_lookup",
})

def _sanitize(text: str, tool_name: str = "") -> str:
    """Strip script/HTML. Truncate only for web-sourced tools (anti prompt-injection).
    Document retrieval tools (read_excerpt, read_pages, read_section) are NOT truncated."""
    text = _SCRIPT_TAG.sub('', text)
    text = _HTML_TAG.sub('', text)
    if tool_name in _WEB_TOOLS:
        return text[:MAX_RESEARCH_EXCERPT_CHARS]
    return text


# ── BaseAgent ─────────────────────────────────────────────────────────────────

class BaseAgent:
    def __init__(
        self,
        manifest: AgentManifest,
        registry: ToolRegistry,
        hook_engine: HookEngine,
        tool_definitions: list[dict],
        workflow: str | None = None,
    ):
        self.manifest         = manifest
        self.registry         = registry
        self.hook_engine      = hook_engine
        self.tool_definitions = tool_definitions
        self.workflow         = workflow
        # Use plugin_id as the role key for model routing.
        # When constructed via PluginManifest.to_agent_manifest(), plugin_id IS the role.
        self.model            = get_model(manifest.plugin_id, workflow)
        self._client          = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # ── Public entry point ────────────────────────────────────────────────────

    def run(
        self,
        system_prompt: str,
        messages: list[dict],
        context: dict,
        require_citations: bool = False,
    ) -> dict:
        """Run the agentic loop. Returns {'text': str, 'tool_calls': list}."""
        start      = time.time()
        turns      = 0
        tool_calls = []
        msgs       = list(messages)

        while True:
            # ── timeout check ────────────────────────────────────────────────
            elapsed = time.time() - start
            if elapsed > self.manifest.timeout_seconds:
                raise AgentTimeoutError(
                    f"{self.manifest.plugin_id} timed out after {elapsed:.0f}s "
                    f"(limit: {self.manifest.timeout_seconds}s)"
                )

            # ── turn limit ───────────────────────────────────────────────────
            if turns >= self.manifest.max_turns:
                raise MaxTurnsError(
                    f"{self.manifest.plugin_id} reached max turns ({self.manifest.max_turns})"
                )

            # ── API call with retry ──────────────────────────────────────────
            response = self._call_api(system_prompt, msgs)
            turns   += 1

            # ── handle tool_use ──────────────────────────────────────────────
            if response.stop_reason == "tool_use":
                tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
                tool_results    = []

                for block in tool_use_blocks:
                    result = self._dispatch_tool(block.name, block.input)
                    tool_calls.append({"tool": block.name, "input": block.input, "result": result})
                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,
                        "content":     _sanitize(str(result), block.name),
                    })

                msgs.append({"role": "assistant", "content": response.content})
                msgs.append({"role": "user",      "content": tool_results})
                continue

            # ── end_turn — extract final text ────────────────────────────────
            text = "".join(
                b.text for b in response.content if hasattr(b, "text")
            )

            # ── citation guard ───────────────────────────────────────────────
            # In live mode: enforce that at least one authoritative tool was called.
            # In knowledge_only mode: authoritative tools return stubs, so the hard
            # block is skipped. A disclaimer is appended to the output instead.
            if require_citations and RESEARCH_MODE == "live":
                has_citations = any(
                    tc["tool"] in ("regulatory_lookup", "sanctions_check", "company_lookup")
                    for tc in tool_calls
                )
                if not has_citations:
                    raise NoCitationsError(
                        f"{self.manifest.plugin_id} produced no authoritative citations "
                        "but workflow requires them."
                    )
            elif require_citations and RESEARCH_MODE != "live":
                text = (
                    text + "\n\n"
                    "[Knowledge-only mode: no authoritative citations fetched. "
                    "Output based on model knowledge and knowledge-base files. "
                    "Verify regulatory references independently before client delivery.]"
                )

            return {"text": text, "tool_calls": tool_calls}

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _call_api(self, system_prompt: str, messages: list[dict]) -> Any:
        """Call Anthropic API with exponential backoff retry."""
        kwargs = dict(
            model=self.model,
            max_tokens=getattr(self.manifest, "max_tokens", 8192),
            system=system_prompt,
            messages=messages,
        )
        if self.tool_definitions:
            kwargs["tools"] = self.tool_definitions

        last_error = None
        for attempt, backoff in enumerate(RETRY_BACKOFF_SECONDS):
            try:
                return self._client.messages.create(**kwargs)
            except anthropic.RateLimitError as e:
                last_error = e
                if attempt < MAX_API_RETRIES - 1:
                    time.sleep(backoff)
            except anthropic.APIStatusError as e:
                # non-retryable
                raise
        raise last_error

    def _dispatch_tool(self, name: str, inputs: dict) -> Any:
        """Dispatch a tool call through the registry, enforcing manifest permissions."""
        return self.registry.call(name, self.manifest.required_tools, **inputs)
