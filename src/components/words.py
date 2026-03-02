#!/usr/bin/env python

import pygame
from enum import Enum

class TextType(Enum):
    NORMAL = 1
    ACTIVE = 2
    INTERCALATED = 3
    INSTRUCTION = 4
    INDEX = 5
    DEFINITION = 6
    CONCEPT = 7
    TEXT_BOX = 8

class FontManager:
    """Cache of pygame Font objects keyed by (size, bold, underline)."""

    def __init__(self):
        """Initialise the font cache using FreeSans as the default typeface."""
        self.fonts = {}
        self.default_font = pygame.font.match_font("FreeSans", False, False)

    def get_font(self, size, bold=False, underline=False):
        """
        Return a cached Font for the given style, creating it on first use.

        @param size: Point size of the font.
        @type size: int
        @param bold: Whether the font should be bold.
        @type bold: bool
        @param underline: Whether the font should be underlined.
        @type underline: bool
        @return: Configured font object.
        @rtype: pygame.font.Font
        """
        key = (size, bold, underline)
        if key not in self.fonts:
            font = pygame.font.Font(self.default_font, size)
            font.set_bold(bold)
            font.set_underline(underline)
            self.fonts[key] = font
        return self.fonts[key]
    
font_manager = FontManager()

class Word(pygame.sprite.Sprite):
    """Rendered word sprite that supports glossary lookup and keyboard-navigation highlighting.

    Class-level glossary dictionaries (ENTRIES, DEFINITIONS, INDICES, INTERCALATED) are
    populated at startup by Manejador from content.json.
    """

    # Populated at startup by Manejador.load_text_content() from content.json "glossary".
    ENTRIES: dict = {}
    DEFINITIONS: dict = {}
    INDICES: list = []
    INTERCALATED: list = []

    def __init__(self, text, size, text_type, font_manager=font_manager):
        """
        Initialise and render the word sprite.

        @param text: The word or token to display.
        @type text: str
        @param size: Base font size in points.
        @type size: int
        @param text_type: Rendering role; must be a valid TextType int value.
        @type text_type: int
        @param font_manager: Font cache used to obtain the correct typeface.
        @type font_manager: FontManager
        """
        super().__init__()
        self.text = text
        self.size = size
        self.text_type = TextType(text_type)
        self.font_manager = font_manager
        self.selected = False
        self.definable = False
        self.definition = False
        self.interpretable = False
        self.obj_type = "word"

        self.clean_text = self.clean_word(text)
        self.code = self.get_code()
        self.render()

    def get_code(self):
        """Return the glossary code for this word, or an empty string if none exists."""
        if self.clean_text in self.ENTRIES:
            return self.ENTRIES[self.clean_text]
        elif self.text_type == TextType.DEFINITION:
            return self.DEFINITIONS.get(self.text, "")
        return ""

    def render(self):
        """Re-render the word surface using the current style flags and selection state."""
        bold = self.text_type in [TextType.INDEX, TextType.INSTRUCTION] or (self.text_type == TextType.DEFINITION and self.selected)
        underline = self.text_type == TextType.NORMAL and self.clean_text in self.ENTRIES

        font = self.font_manager.get_font(self.size, bold, underline)

        if self.text_type == TextType.INDEX:
            color = (122, 140, 31) if self.clean_text in self.INDICES else (60, 36, 21)
        else:
            color = (0, 0, 0) if self.text_type in [TextType.NORMAL, TextType.ACTIVE, TextType.INTERCALATED, TextType.INSTRUCTION] else (60, 36, 21)

        self.image = font.render(self.text, True, color)
        self.rect = self.image.get_rect()

        self.update_flags()

    def update_flags(self):
        """Recompute interpretable, definable, and definition flags from the current state."""
        self.interpretable = self.text_type == TextType.NORMAL and self.clean_text in self.ENTRIES
        self.definable = self.text_type == TextType.INDEX and self.clean_text in self.INDICES
        self.definition = self.text_type == TextType.DEFINITION and self.clean_text in self.DEFINITIONS

    def highlight(self):
        """Enlarge and bold this word if it is an INDEX type and not already selected."""
        if self.text_type == TextType.INDEX and not self.selected:
            self.selected = True
            self.size += 6
            self.render()

    def restore(self):
        """Revert to normal size and weight if this word is an INDEX type and currently selected."""
        if self.text_type == TextType.INDEX and self.selected:
            self.selected = False
            self.size -= 6
            self.render()

    def update(self, update_type):
        """
        Deselect and re-render DEFINITION or INDEX words on scroll events.

        @param update_type: Scroll direction code (1 = scroll up, 2 = scroll down).
        @type update_type: int
        """
        if update_type in [1, 2] and self.text_type in [TextType.DEFINITION, TextType.INDEX]:
            self.selected = False
            self.render()

    def get_reader_text(self):
        """Text spoken by the screen reader when this word is focused."""
        return "explicar la palabra:" + self.text

    @staticmethod
    def clean_word(word):
        """
        Strip leading and trailing punctuation from a word.

        @param word: Raw word token, possibly surrounded by punctuation.
        @type word: str
        @return: Word with surrounding punctuation removed.
        @rtype: str
        """
        return word.strip(".,()¿?¡!")
