#!/usr/bin/env python3

import pygame


class SpriteSheet:
    """
    Loads a sprite-sheet image and extracts individual frames from it.

    Used by both ``Animation`` (multi-row sheets) and ``Button``
    (single-row sheets).  The ``load_strip`` method unifies both use cases
    through optional ``rows`` and ``row`` parameters that default to
    single-row behaviour so existing Button call-sites need minimal changes.
    """

    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error:
            raise SystemExit

    def image_at(self, rectangle, colorkey=None):
        """
        Extract a single frame at the given rectangle.

        @param rectangle: (x, y, w, h) of the frame within the sheet.
        @type  rectangle: tuple | pygame.Rect
        @param colorkey:  Colour treated as transparent.  Pass -1 to use the
                          top-left pixel of the frame.  None = no transparency.
        @type  colorkey:  tuple | int | None
        @return: Extracted surface.
        @rtype:  pygame.Surface
        """
        rect = pygame.Rect(rectangle)
        image = self.sheet.subsurface(rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image

    def images_at(self, rects, colorkey=None):
        """
        Extract multiple frames from a list of rectangles.

        @param rects:    Sequence of (x, y, w, h) tuples, one per frame.
        @type  rects:    list
        @param colorkey: Colour treated as transparent (see image_at).
        @type  colorkey: tuple | int | None
        @return: List of extracted surfaces.
        @rtype:  list[pygame.Surface]
        """
        return [self.image_at(rect, colorkey) for rect in rects]

    def load_strip(self, rect, image_count, rows=1, row=0, colorkey=None):
        """
        Extract a horizontal strip of equally-sized frames.

        Single-row usage (Button)::

            sheet.load_strip(rect, frame_count, colorkey=colorkey)

        Multi-row usage (Animation)::

            sheet.load_strip(rect, col, rows=fil, row=fila_pos, colorkey=ck)

        @param rect:        Source rect for the *first* frame — (x, y, w, h).
        @type  rect:        tuple | pygame.Rect
        @param image_count: Number of frames to extract.
        @type  image_count: int
        @param rows:        Total number of rows in the sheet (≥ 1).
                            When 1 (the default) the frame y-coordinate is
                            taken directly from *rect*.
        @type  rows:        int
        @param row:         Zero-based index of the row to read (0 = top row).
        @type  row:         int
        @param colorkey:    Colour treated as transparent (see image_at).
        @type  colorkey:    tuple | int | None
        @return: List of frame surfaces in left-to-right order.
        @rtype:  list[pygame.Surface]
        """
        if rows <= 1:
            tups = [
                (rect[0] + rect[2] * x, rect[1], rect[2], rect[3])
                for x in range(image_count)
            ]
        else:
            tups = [
                (rect[0] + rect[2] * x, rect[1] + row * rect[3], rect[2], rect[3])
                for x in range(image_count)
            ]
        return self.images_at(tups, colorkey)
