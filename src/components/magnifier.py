#!/usr/bin/env python

import pygame


class Magnifier(pygame.sprite.Sprite):
    """Screen magnifier sprite that zooms a region of the display around the cursor."""

    def __init__(self):
        """Initialise the magnifier with default zoom level and a 256×256 pixel viewport."""
        pygame.sprite.Sprite.__init__(self)
        self.escala = 1
        self.zoom = 1
        self.w = 256
        self.h = 256
        self.cxp = 1024
        self.cyp = 572
        self.ampliador = pygame.Surface((self.w, self.h))
        self.sup_final = pygame.Surface
        self.rect = pygame.Rect((0, 232), (self.w, self.h))

    def _sample_surface(self, surface, x, y):
        """
        Clamp the cursor to the screen boundary and blit the sampled region into ``self.ampliador``.

        The source region is centred on (x, y) with dimensions ``(w/zoom, h/zoom)``.
        Clamping prevents sampling outside the screen edges.

        @param surface: Full display surface to sample from.
        @type surface: pygame.Surface
        @param x: Raw cursor X position in pixels.
        @type x: int
        @param y: Raw cursor Y position in pixels.
        @type y: int
        """
        half_w = self.w / (2 * self.zoom)
        half_h = self.h / (2 * self.zoom)
        x = min(max(x, half_w), self.cxp - half_w)
        y = min(max(y, half_h), self.cyp - half_h)
        self.ampliador = pygame.Surface((self.w / self.zoom, self.h / self.zoom))
        self.ampliador.blit(
            surface,
            (0, 0),
            (x - half_w, y - half_h, self.w / self.zoom, self.h / self.zoom),
        )

    def magnificar(self, surface):
        """
        Capture and scale the screen region around the cursor into the magnifier surface.

        @param surface: Full display surface to sample from.
        @type surface: pygame.Surface
        """
        x, y = pygame.mouse.get_pos()
        if self.escala >= 3 and self.zoom >= 4:
            self.escala = 3
            self.zoom = 4
        elif self.escala <= 1 and self.zoom <= 1:
            self.escala = 1
            self.zoom = 1

        self._sample_surface(surface, x, y)

        if self.escala == 1:
            self.sup_final = self.ampliador
        elif self.escala == 2:
            sup_escalax2 = pygame.transform.scale2x(self.ampliador)
            self.sup_final = pygame.transform.smoothscale(sup_escalax2, (self.w, self.h))
        elif self.escala == 3:
            sup_escalax2 = pygame.transform.scale2x(self.ampliador)
            sup_escalax4 = pygame.transform.scale2x(sup_escalax2)
            self.sup_final = pygame.transform.smoothscale(sup_escalax4, (self.w, self.h))
        self.image = self.sup_final

    def zoom_in(self):
        """Increase the magnifier zoom level by one step."""
        self.escala = self.escala + 1
        self.zoom = (2**self.escala) / 2

    def zoom_out(self):
        """Decrease the magnifier zoom level by one step."""
        self.escala = self.escala - 1
        self.zoom = self.zoom / 2


class Rendermag(pygame.sprite.Group):
    """Sprite group that draws the magnifier and overlays a black rectangle when it is being repositioned."""

    def draw(self, surface, mov):
        """
        Draw the magnifier sprites onto the surface.

        @param surface: Surface to draw onto.
        @type surface: pygame.Surface
        @param mov: If True, fill the magnifier rect with black to indicate it is being moved.
        @type mov: bool
        """
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sprites:
            self.spritedict[spr] = surface_blit(spr.image, spr.rect)
            pygame.draw.rect(surface, (0, 0, 0), spr.rect, 2)
            if mov:
                pygame.draw.rect(surface, (0, 0, 0), spr.rect)
