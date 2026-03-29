from typing import Any, Callable

Hook = Callable[[dict, dict], dict]


class HookVetoError(Exception):
    """Raised by a hook to block the pipeline. Message is shown to the user."""
    def __init__(self, hook_name: str, reason: str):
        self.hook_name = hook_name
        self.reason = reason
        super().__init__(f"[{hook_name}] blocked: {reason}")


class HookEngine:
    """Chain-of-responsibility runner for pre and post hooks.

    Hooks are pure functions: (payload: dict, context: dict) -> dict
    A hook may mutate and return the payload, or raise HookVetoError to block.
    """

    def __init__(self):
        self._pre_hooks:  list[tuple[str, Hook]] = []
        self._post_hooks: list[tuple[str, Hook]] = []

    def register_pre(self, name: str, fn: Hook) -> None:
        self._pre_hooks.append((name, fn))

    def register_post(self, name: str, fn: Hook) -> None:
        self._post_hooks.append((name, fn))

    def run_pre(self, payload: dict, context: dict) -> dict:
        """Run all pre-hooks in order. Raises HookVetoError on first blocking hook."""
        for name, fn in self._pre_hooks:
            payload = fn(payload, context)
        return payload

    def run_post(self, payload: dict, context: dict) -> dict:
        """Run all post-hooks in order. Raises HookVetoError on first blocking hook."""
        for name, fn in self._post_hooks:
            payload = fn(payload, context)
        return payload
