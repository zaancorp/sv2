#!/usr/bin/env python
# Backwards-compatible alias — Boundary is now CollidableZone.
from .collidable_zone import CollidableZone as Boundary

__all__ = ["Boundary"]
