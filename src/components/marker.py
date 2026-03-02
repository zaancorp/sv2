#!/usr/bin/env python

import pygame


class Marker(pygame.sprite.Sprite):
    """Target marker sprite used in activity 1 to define drop zones."""

    def __init__(self, rect, id):
        """
        Initialise the marker sprite.

        @param rect: Rectangle defining the position and size of the marker.
        @type rect: pygame.Rect
        @param id: Identifier for this marker.
        @type id: str
        """
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(rect)
        self.id = id
