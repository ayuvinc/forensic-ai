"""Central tool registry and dispatcher.

Tools are registered by name. Agents may only call tools declared in their
manifest's required_tools list — any other call raises ToolNotAllowedError.
"""

from typing import Any, Callable

ToolFn = Callable[..., Any]


class ToolNotFoundError(Exception):
    pass


class ToolNotAllowedError(Exception):
    pass


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolFn] = {}

    def register(self, name: str, fn: ToolFn) -> None:
        """Register a tool function under a given name."""
        self._tools[name] = fn

    def call(self, tool_name: str, allowed_tools: list[str], **kwargs: Any) -> Any:
        """Dispatch a tool call.

        Raises ToolNotAllowedError if the agent's manifest doesn't include the tool.
        Raises ToolNotFoundError if the tool isn't registered.
        """
        if tool_name not in allowed_tools:
            raise ToolNotAllowedError(
                f"Tool '{tool_name}' is not in the agent's allowed tools: {allowed_tools}"
            )
        if tool_name not in self._tools:
            raise ToolNotFoundError(f"Tool '{tool_name}' is not registered.")
        return self._tools[tool_name](**kwargs)

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())


# ── Global singleton ──────────────────────────────────────────────────────────
registry = ToolRegistry()
