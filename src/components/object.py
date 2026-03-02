#!/usr/bin/env python3

from pygame import Rect

from pygame.image import load
from pygame.sprite import Sprite
from pygame.transform import smoothscale


class GameObject(Sprite):
    """Base sprite class that loads an image asset and positions it on screen."""

    def __init__(self, x, y, imagen, name):
        """
        Load the image asset and place the sprite at the given coordinates.

        @param x: X coordinate at which to draw the sprite.
        @type x: int
        @param y: Y coordinate at which to draw the sprite.
        @type y: int
        @param imagen: Path to the image file to load.
        @type imagen: str
        @param name: Name identifier for this game object.
        @type name: str
        """
        Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = load(imagen).convert_alpha()
        self.rect = Rect(
            self.x, self.y, self.image.get_width(), self.image.get_height()
        )

    def get_center(self):
        """
        Return the horizontal centre of the sprite in screen coordinates.

        @return: X coordinate of the sprite's horizontal centre.
        @rtype: int
        """

        (_, _, width, _) = self.image.get_rect()
        return int(self.x + (width / 2.0))

    def relocate(self, x=None, y=None):
        """
        Move the sprite to new coordinates without recreating it.

        @param x: New X coordinate; unchanged if omitted.
        @type x: int
        @param y: New Y coordinate; unchanged if omitted.
        @type y: int
        """

        if x:
            self.rect.x = x
        if y:
            self.rect.y = y

    def resize(self, width=None, height=None):
        """
        Rescale the sprite image, resetting to the original first.

        @param width: New width in pixels; uses current width if omitted.
        @type width: int
        @param height: New height in pixels; uses current height if omitted.
        @type height: int
        """

        self.image = self._original

        if not width:
            (_, _, width, _) = self.image.get_rect()

        if not height:
            (_, _, height, _) = self.image.get_rect()

        self.image = smoothscale(self.image, (width, height))

    def set_center(self, x, y):
        self.rect.center = (x, y)


class PropObject(GameObject):
    """Interactive prop sprite used in activity 1; carries an increase value for the character image state."""

    # Maps each prop name to its image-state increment for the character class.
    aumentos = {
        "la carretilla. ": 1,
        "las semillas. ": 1,
        "la regadera. ": 2,
        "la pala. ": 4,
        "el abono. ": 8,
        "el controlador biológico. ": 16,
    }

    def __init__(self, x, y, imagen, name):
        """
        Load the prop image and look up its increase value.

        @param x: X coordinate at which to draw the prop.
        @type x: int
        @param y: Y coordinate at which to draw the prop.
        @type y: int
        @param imagen: Path to the prop image file.
        @type imagen: str
        @param name: Prop name; must be a key in the `aumentos` dict.
        @type name: str
        """

        Sprite.__init__(self)
        self.name = name
        self.x = x
        self.y = y
        self.image = load(imagen).convert_alpha()
        self.rect = Rect(
            self.x, self.y, self.image.get_width(), self.image.get_height()
        )
        self.aumento = self.aumentos[name]
