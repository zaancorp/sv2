#!/usr/bin/env python

import pygame


class Cursor(pygame.sprite.Sprite):
    """Sprite that tracks the mouse cursor position each frame."""

    def __init__(self):
        """Initialise the cursor sprite with a 1×1 pixel rect."""
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(0, 0, 1, 1)

    def update(self):
        """Sync the sprite rect to the current mouse position."""
        self.rect.left, self.rect.top = pygame.mouse.get_pos()
