#!/usr/bin/env python
"""Pixel-perfect sprite collision detection using alpha hitmasks."""


def _pixelPerfectCollisionDetection(sp1, sp2):
    """
    Test whether two sprites overlap at the pixel level using their hitmasks.

    @param sp1: First sprite; must have a rect and a hitmask array.
    @type sp1: pygame.sprite.Sprite
    @param sp2: Second sprite; must have a rect and a hitmask array.
    @type sp2: pygame.sprite.Sprite
    @return: True if any overlapping pixels are both non-transparent.
    @rtype: bool
    """
    rect1 = sp1.rect
    rect2 = sp2.rect
    rect = rect1.clip(rect2)
    hm1 = sp1.hitmask
    hm2 = sp2.hitmask
    x1 = rect.x - rect1.x
    y1 = rect.y - rect1.y
    x2 = rect.x - rect2.x
    y2 = rect.y - rect2.y
    for r in range(0, rect.height):
        for c in range(0, rect.width):
            if hm1[c + x1][r + y1] & hm2[c + x2][r + y2]:
                return True
    return False


def spritecollide_pp(sprite, group):
    """
    Return all sprites in group that collide pixel-perfectly with sprite.

    Each sprite must expose a rect and a 2-D hitmask array (e.g. from
    pygame.surfarray.array_alpha()).

    @param sprite: Sprite to test against the group.
    @type sprite: pygame.sprite.Sprite
    @param group: Group of sprites to check.
    @type group: pygame.sprite.Group
    @return: List of sprites that overlap sprite at the pixel level.
    @rtype: list
    """
    crashed = []
    spritecollide = sprite.rect.colliderect
    ppcollide = _pixelPerfectCollisionDetection
    for s in group.sprites():
        if spritecollide(s.rect):
            if ppcollide(sprite, s):
                crashed.append(s)
    return crashed
