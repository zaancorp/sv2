#!/usr/bin/env python3
"""Safe nested accessor for the project's JSON text content."""

from __future__ import annotations

from typing import Any, Dict, Optional


class TextLoader:
    """Convenience accessor for nested text content loaded from JSON."""

    def __init__(self, content: Optional[Dict[str, Any]]):
        """
        Initialise the loader with the parsed JSON dictionary.

        @param content: Top-level dict from the content JSON file; treated as empty if None.
        @type content: dict | None
        """
        self._content: Dict[str, Any] = content or {}

    def get(self, *keys: str, default: Any = None) -> Any:
        """
        Traverse nested keys and return the value, or default if any key is missing.

        @param keys: Sequence of string keys to traverse.
        @param default: Value returned when a key is absent.
        @return: Value at the given path, or default.
        """
        cur: Any = self._content
        for k in keys:
            if not isinstance(cur, dict) or k not in cur:
                return default
            cur = cur[k]
        return cur

    def require(self, *keys: str) -> Any:
        """
        Traverse nested keys and return the value, raising KeyError if any key is missing.

        @param keys: Sequence of string keys to traverse.
        @return: Value at the given path.
        @raises KeyError: If any key in the path does not exist.
        """
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
        """
        Return the content dict for a specific screen.

        @param screen_id: Key under the top-level "content" section (e.g. "screen_3").
        @type screen_id: str
        @return: Dict of text keys for that screen.
        @rtype: dict
        """
        return self.require("content", screen_id)

    def popup(self, screen_id: str, key: str) -> str:
        """
        Return a popup string for the given screen and key.

        @param screen_id: Screen identifier within the "popups" section.
        @type screen_id: str
        @param key: Key within that screen's popup section.
        @type key: str
        @return: Popup text string.
        @rtype: str
        """
        return self.require("popups", screen_id, key)

    def concept(self, concept_id: str) -> str:
        """
        Return the definition string for a glossary concept.

        @param concept_id: Key within the "concepts" section.
        @type concept_id: str
        @return: Concept definition string.
        @rtype: str
        """
        return self.require("concepts", concept_id)

    def ui(self, *keys: str, default: Any = None) -> Any:
        """
        Return a UI string by traversing keys under the top-level "ui" section.

        @param keys: Sub-keys within the "ui" section.
        @param default: Value returned when a key is absent.
        @return: UI string, or default if not found.
        """
        return self.get("ui", *keys, default=default)

