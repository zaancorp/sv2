#!/usr/bin/env python

import sys
import pygame


class EventHandler:
    """Event handler that collects pressed and held key states each frame."""

    def __init__(self):
        """Initialise the event handler with empty key and modifier state lists."""
        self.keyspressed = []
        self.keys = []
        self.mods = []

    def update(self):
        """Poll the pygame event queue and update the key and modifier states."""
        self.event = pygame.event.get()
        for event in self.event:
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                if event.key not in self.keys:
                    self.keys.append(event.key)
            if event.type == pygame.KEYUP:
                if event.key in self.keys:
                    self.keys.remove(event.key)
        self.get_pressed()

    def get_pressed(self):
        """Refresh the held-key bitmask and the active modifier flags."""
        self.keyspressed = pygame.key.get_pressed()
        self.mods = pygame.key.get_mods()

    def pressed(self, key):
        """
        Check whether a key was pressed this frame.

        @param key: pygame key constant to test.
        @type key: int
        @return: True if the key was pressed, False otherwise.
        @rtype: bool
        """
        if key in self.keys:
            return True
        else:
            return False

    def held(self, key):
        """
        Check whether a key is currently being held down.

        @param key: pygame key constant to test.
        @type key: int
        @return: True if the key is held, False otherwise.
        @rtype: bool
        """

        if self.keyspressed[key]:
            return True
        else:
            return False

    def modded(self, key):
        """
        Check whether a modifier key is currently active.

        @param key: pygame modifier constant (e.g. pygame.KMOD_CTRL) to test.
        @type key: int
        @return: True if the modifier is active, False otherwise.
        @rtype: bool
        """
        if self.mods & key:
            return True
        else:
            return False
