#!/usr/bin/env python

import pygame


class CollidableZone(pygame.sprite.Sprite):
    """Invisible collidable rectangle sprite used in activity screens.

    Replaces the former ``Marker`` (drop-zone target) and ``Boundary``
    (wall collision) classes, which were structurally identical.  Callers
    that imported ``Marker`` or ``Boundary`` by name still work via the
    backwards-compatible aliases in ``marker.py`` and ``boundary.py``.

    @param rect: Rectangle defining the position and size of the zone.
    @type rect: tuple | pygame.Rect
    @param id: Identifier for this zone (string name or integer number).
    @type id: str | int
    """

    def __init__(self, rect, id):
        """
        Initialise the collidable zone sprite.

        @param rect: Rectangle defining the position and size of the zone.
        @type rect: tuple | pygame.Rect
        @param id: Identifier for this zone.
        @type id: str | int
        """
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.id = id
