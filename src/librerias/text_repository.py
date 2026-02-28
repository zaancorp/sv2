#!/usr/bin/env python3

import json
import os
from functools import lru_cache
from typing import Any, Dict, Optional


def _src_dir() -> str:
    # /.../src/librerias -> /.../src
    return os.path.dirname(os.path.abspath(os.path.dirname(__file__)))


def default_content_path() -> str:
    return os.path.join(_src_dir(), "paginas", "text", "content.json")


@lru_cache(maxsize=1)
def load_text_content(path: Optional[str] = None) -> Dict[str, Any]:
    """
    Loads the project's text content JSON and caches it.
    """
    content_path = path or default_content_path()
    with open(content_path, "r", encoding="utf-8") as f:
        return json.load(f)


def invalidate_text_cache() -> None:
    load_text_content.cache_clear()

