#!/usr/bin/env python3

from pygame import Rect, Surface

from pygame.image import load
from pygame.sprite import Sprite

from .object import GameObject


class Image(GameObject):
    """Sprite that loads a single image file and places it at a given screen position."""

    # Backup of the original surface
    _original = Surface((0, 0))

    def __init__(self, x, y, image):
        """
        Load an image and position it on screen.

        @param x: X coordinate at which to draw the image.
        @type x: int
        @param y: Y coordinate at which to draw the image.
        @type y: int
        @param image: Path to the image file to load.
        @type image: str
        """

        Sprite.__init__(self)

        self.image = load(image).convert_alpha()
        self._original = self.image
        (_, _, width, height) = self.image.get_rect()
        self.rect = Rect(x, y, width, height)
