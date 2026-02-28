#!/usr/bin/env python3

from __future__ import annotations

from typing import Any, Dict, Optional


class TextLoader:
    """
    Convenience accessor for nested text content loaded from JSON.
    """

    def __init__(self, content: Optional[Dict[str, Any]]):
        self._content: Dict[str, Any] = content or {}

    def get(self, *keys: str, default: Any = None) -> Any:
        cur: Any = self._content
        for k in keys:
            if not isinstance(cur, dict) or k not in cur:
                return default
            cur = cur[k]
        return cur

    def require(self, *keys: str) -> Any:
        cur: Any = self._content
        walked = []
        for k in keys:
            walked.append(k)
            if not isinstance(cur, dict) or k not in cur:
                raise KeyError("Missing text key: " + ".".join(walked))
            cur = cur[k]
        return cur

    # Common shortcuts used throughout the project
    def screen_content(self, screen_id: str) -> Dict[str, Any]:
        return self.require("content", screen_id)

    def popup(self, screen_id: str, key: str) -> str:
        return self.require("popups", screen_id, key)

    def concept(self, concept_id: str) -> str:
        return self.require("concepts", concept_id)

    def ui(self, *keys: str, default: Any = None) -> Any:
        return self.get("ui", *keys, default=default)

