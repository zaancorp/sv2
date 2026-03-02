#!/usr/bin/env python

import pygame

from components.spritesheet import SpriteSheet


class Animation(pygame.sprite.Sprite):
    """Sprite that plays a frame-strip animation at a configurable speed."""

    def __repr__(self) -> str:
        return repr(
            "Animation({}, {}, {}, {}, {}, {}, {})".format(
                self.id, self.filename, self.col, self.rows, self.ck, self.loop, self.f
            )
        )

    def __init__(
        self, id, filename, col, rows, x, y, colorkey=None, loop=False, frames=1
    ):
        """
        Initialise the animation sprite.

        @param id: Unique identifier for this animation instance.
        @type id: str
        @param filename: Path to the sprite-sheet image.
        @type filename: str
        @param col: Number of columns in the sprite sheet.
        @type col: int
        @param rows: Number of rows in the sprite sheet.
        @type rows: int
        @param x: X coordinate at which to draw the animation.
        @type x: int
        @param y: Y coordinate at which to draw the animation.
        @type y: int
        @param colorkey: Colour treated as transparent; omit if not needed.
        @type colorkey: tuple
        @param loop: If True the animation loops; if False it plays once.
        @type loop: bool
        @param frames: Number of game ticks per frame; 1 is the fastest.
        @type frames: int
        """
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.col = col
        self.rows = rows
        self.obj_type = "animation"
        self.filename = filename
        self.ss = SpriteSheet(filename)
        (_, _, w, h) = self.ss.sheet.get_rect()
        self.ck = colorkey
        self.frame_row = 0
        self.rect = pygame.Rect(x, y, w / col, h / rows)
        self.rt = pygame.Rect(0, 0, w / col, h / rows)
        self.images = self.ss.load_strip(self.rt, col, rows, self.frame_row, colorkey)
        self.i = 0
        self.loop = loop
        self.frames = frames
        self.f = frames
        self.image = pygame.Surface((0, 0))
        self.img = self.images[0]
        self.stop = False

    def update(self):
        """Reset the animation to its first frame."""
        self.i = 0
        self.image = self.images[0]
        self.stop = True

    def set_frame(self, row):
        """
        Switch the active sprite-sheet row.

        @param row: Row index to display.
        @type row: int
        """
        self.frame_row = row
        self.images = self.ss.load_strip(
            self.rt, self.col, self.rows, self.frame_row, self.ck
        )

    def move(self, x):
        """
        Move the animation to a new X position.

        @param x: New X coordinate.
        @type x: int
        """
        (_, y, w, h) = self.rect
        self.rect = pygame.Rect(x, y, w, h)

    def reposition(self, x, y):
        """
        Move the animation to a new X and Y position.

        @param x: New X coordinate.
        @type x: int
        @param y: New Y coordinate.
        @type y: int
        """
        (_, _, w, h) = self.image.get_rect()
        self.rect = pygame.Rect(x, y, w, h)

    def set_speed(self, speed):
        """
        Set the frame speed (ticks per frame).

        @param speed: New ticks-per-frame value; 1 is the fastest.
        @type speed: int
        """
        self.f = speed
        self.frames = speed

    def detener(self):
        """Stop the animation and reset to the first frame."""
        self.stop = True
        self.image = self.images[0]
        self.i = 0

    def continuar(self):
        """Resume a stopped animation."""
        self.stop = False

    def repetir(self):
        """Restart a non-looping animation from the first frame."""
        self.stop = False
        self.i = 0

    def next(self):
        """Advance the animation by one tick, updating the displayed frame."""
        if self.i >= len(self.images):
            if not self.loop:
                self.stop = True
            else:
                self.i = 0
        if not self.stop:
            self.image = self.images[self.i]
            self.f -= 1
            if self.f == 0:
                self.i += 1
                self.f = self.frames


class RenderAnim(pygame.sprite.Group):
    """Sprite group that advances each Animation member's frame on every draw call."""

    def draw(self, surface):
        """
        Draw all member sprites and advance their frames.

        @param surface: Surface to draw onto.
        @type surface: pygame.Surface
        """
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sprites:
            self.spritedict[spr] = surface_blit(spr.image, spr.rect)
            spr.next()
