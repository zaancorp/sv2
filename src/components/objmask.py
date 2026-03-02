#!/usr/bin/env python

import pygame


class object_mask(pygame.sprite.Sprite):
    """Pixel-perfect collidable sprite used for interactive map areas."""

    def __init__(self, id, x, y, img1, img2=""):
        """
        Initialise the sprite with active and inactive images.

        @param id: Unique identifier; also used as the screen-reader label.
        @type id: str
        @param x: Left position of the sprite on screen.
        @type x: int
        @param y: Top position of the sprite on screen.
        @type y: int
        @param img1: Path to the active (highlighted) image.
        @type img1: str
        @param img2: Path to the inactive image; defaults to img1 when omitted.
        @type img2: str
        """
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.obj_type = "map"
        self.image = pygame.image.load(img1)
        if not img2 == "":
            self.image_act = pygame.image.load(img2)
        else:
            self.image_act = self.image
        self.image_des = self.image
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
        self.hitmask = pygame.surfarray.array_alpha(self.image)

    def get_reader_text(self):
        """Text spoken by the screen reader when this map area is focused."""
        return self.id

    def iluminar(self):
        """Switch to the active (highlighted) image."""
        self.image = self.image_act

    def apagar(self):
        """Switch to the inactive image."""
        self.image = self.image_des
