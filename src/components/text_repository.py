#!/usr/bin/env python3
"""Functions for locating and loading the project's text content JSON file."""

import json
import os
from functools import lru_cache
from typing import Any, Dict, Optional


def _src_dir() -> str:
    # /.../src/librerias -> /.../src
    return os.path.dirname(os.path.abspath(os.path.dirname(__file__)))


def content_path_for_language(lang: str) -> str:
    """
    Return the absolute path to the content JSON file for the given language code.

    @param lang: BCP 47-style language code (e.g. "es", "hu").
    @type lang: str
    @return: Absolute path to content-{lang}.json.
    @rtype: str
    """
    filename = f"content-{lang}.json"
    return os.path.join(_src_dir(), "paginas", "text", filename)


def default_content_path() -> str:
    """Return the absolute path to the default (Spanish) content JSON file."""
    return content_path_for_language("es")


@lru_cache(maxsize=1)
def load_text_content(path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load and LRU-cache the project's text content JSON.

    @param path: Absolute path to the JSON file; defaults to the Spanish content file.
    @type path: str | None
    @return: Parsed content dictionary.
    @rtype: dict
    """
    content_path = path or default_content_path()
    with open(content_path, "r", encoding="utf-8") as f:
        return json.load(f)


def invalidate_text_cache() -> None:
    """Clear the load_text_content LRU cache, forcing the next call to re-read from disk."""
    load_text_content.cache_clear()

