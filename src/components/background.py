#!/usr/bin/env python

import pygame


class Background:
    """Rounded-rectangle background surface with an optional inset border."""

    def __init__(self, width, height, border=3):
        """
        Build the rounded-rectangle surface.

        @param width: Width of the rectangle in pixels.
        @type width: int
        @param height: Height of the rectangle in pixels.
        @type height: int
        @param border: Inset border thickness in pixels; 0 disables the border.
        @type border: int
        """
        x = 0
        y = 0
        corner_radius = 20
        color = (136, 196, 52)
        color2 = (233, 238, 203)
        self.img = pygame.Surface((width, height))
        self.img.fill((255, 255, 0))
        self.img.set_colorkey((255, 255, 0))
        pygame.draw.rect(self.img, color, (x + corner_radius, y, width - corner_radius * 2, height))
        pygame.draw.rect(self.img, color, (x, y + corner_radius, width, height - corner_radius * 2))
        pygame.draw.circle(self.img, color, (x + corner_radius, y + corner_radius), corner_radius)
        pygame.draw.circle(self.img, color, (x + width - corner_radius, y + corner_radius), corner_radius)
        pygame.draw.circle(self.img, color, (x + corner_radius, y + height - corner_radius), corner_radius)
        pygame.draw.circle(
            self.img, color, (x + width - corner_radius, y + height - corner_radius), corner_radius
        )

        if border > 0:
            width -= border * 2
            height -= border * 2
            img2 = pygame.Surface((width, height))
            img2.fill((255, 255, 0))
            img2.set_colorkey((255, 255, 0))
            pygame.draw.rect(img2, color2, (x + corner_radius, y, width - corner_radius * 2, height))
            pygame.draw.rect(img2, color2, (x, y + corner_radius, width, height - corner_radius * 2))
            pygame.draw.circle(img2, color2, (x + corner_radius, y + corner_radius), corner_radius)
            pygame.draw.circle(img2, color2, (x + width - corner_radius, y + corner_radius), corner_radius)
            pygame.draw.circle(img2, color2, (x + corner_radius, y + height - corner_radius), corner_radius)
            pygame.draw.circle(
                img2, color2, (x + width - corner_radius, y + height - corner_radius), corner_radius
            )
            self.img.blit(img2, (border, border))

    def return_imagen(self):
        """
        Return the rendered background surface.

        @return: Surface containing the rounded rectangle.
        @rtype: pygame.Surface
        """
        return self.img
