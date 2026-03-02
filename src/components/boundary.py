#!/usr/bin/env python

import pygame


class Boundary(pygame.sprite.Sprite):
    """Invisible collidable boundary sprite used in activity 1."""

    def __init__(self, rect, id):
        """
        Initialise the boundary sprite.

        @param rect: Rectangle defining the position and size of the boundary.
        @type rect: pygame.Rect
        @param id: Identifier for this boundary.
        @type id: str
        """
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.id = id
