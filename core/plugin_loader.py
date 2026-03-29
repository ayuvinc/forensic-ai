"""Plugin loader — discovers and loads agent/persona manifests from folders."""

from __future__ import annotations

import json
from pathlib import Path

from schemas.plugins import PluginManifest

BASE_DIR     = Path(__file__).parent.parent
AGENTS_DIR   = BASE_DIR / "agents"
PERSONAS_DIR = BASE_DIR / "personas"


class PluginNotFoundError(Exception):
    pass


class PluginLoader:
    def __init__(self):
        self._cache: dict[str, PluginManifest] = {}

    def load(self, plugin_id: str) -> PluginManifest:
        """Load a plugin manifest by plugin_id. Searches agents/ then personas/."""
        if plugin_id in self._cache:
            return self._cache[plugin_id]

        for base in (AGENTS_DIR, PERSONAS_DIR):
            manifest_path = base / plugin_id / "manifest.json"
            if manifest_path.exists():
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest = PluginManifest(**data)
                self._cache[plugin_id] = manifest
                return manifest

        raise PluginNotFoundError(
            f"No manifest.json found for plugin_id='{plugin_id}'. "
            f"Searched: {AGENTS_DIR}, {PERSONAS_DIR}"
        )

    def load_all_agents(self) -> dict[str, PluginManifest]:
        """Load all enabled agent manifests."""
        return self._load_all(AGENTS_DIR, plugin_type="agent")

    def load_all_personas(self) -> dict[str, PluginManifest]:
        """Load all enabled persona manifests."""
        return self._load_all(PERSONAS_DIR, plugin_type="persona")

    def _load_all(self, base_dir: Path, plugin_type: str) -> dict[str, PluginManifest]:
        result: dict[str, PluginManifest] = {}
        if not base_dir.exists():
            return result
        for subdir in sorted(base_dir.iterdir()):
            if not subdir.is_dir():
                continue
            manifest_path = subdir / "manifest.json"
            if not manifest_path.exists():
                continue
            try:
                data = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest = PluginManifest(**data)
                if manifest.enabled and manifest.plugin_type == plugin_type:
                    result[manifest.plugin_id] = manifest
                    self._cache[manifest.plugin_id] = manifest
            except Exception as e:
                print(f"Warning: Could not load manifest at {manifest_path}: {e}")
        return result


# ── Global singleton ──────────────────────────────────────────────────────────
plugin_loader = PluginLoader()
