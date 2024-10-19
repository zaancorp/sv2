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
    def __init__(self):
        self.fonts = {}
        self.default_font = pygame.font.match_font("FreeSans", False, False)

    def get_font(self, size, bold=False, underline=False):
        key = (size, bold, underline)
        if key not in self.fonts:
            font = pygame.font.Font(self.default_font, size)
            font.set_bold(bold)
            font.set_underline(underline)
            self.fonts[key] = font
        return self.fonts[key]
    
font_manager = FontManager()

class palabra(pygame.sprite.Sprite):
    ENTRIES = {
        "absorbe": "absorber",
        "absorber": "absorber",
        "célula": "celula",
        "componentes": "componentes",
        "fotosíntesis": "fotosintesis",
        "germinación": "germinacion",
        "minerales": "minerales",
        "nutrientes": "nutrientes",
        "órgano": "organo",
        "órganos": "organo",
        "reproducción asexual": "rasexual",
        "reproducción sexual": "rsexual",
        "transformación": "transformacion",
        "transporta": "transportar",
    }

    DEFINITIONS = {
        "Absorber": "absorber",
        "Célula": "celula",
        "Componentes": "componentes",
        "Fotosíntesis": "fotosintesis",
        "Germinar": "germinar",
        "Germinación": "germinacion",
        "Mineral": "minerales",
        "Nutriente": "nutrientes",
        "Órgano": "organo",
        "Reproducción asexual": "rasexual",
        "Reproducción sexual": "rsexual",
        "Transformación": "transformacion",
        "Transportar": "transportar",
    }

    INDICES = ["A", "C", "F", "G", "M", "N", "O", "R", "T"]
    INTERCALATED = ["RATON", "DIR", "ENTER"]

    def __init__(self, text, size, text_type, font_manager=font_manager):
        super().__init__()
        self.text = text
        self.size = size
        self.text_type = TextType(text_type)
        self.font_manager = font_manager
        self.selected = False
        self.definable = False
        self.definition = False
        self.interpretable = False

        self.clean_text = self.clean_word(text)
        self.code = self.get_code()
        self.render()

    def get_code(self):
        if self.clean_text in self.ENTRIES:
            return self.ENTRIES[self.clean_text]
        elif self.text_type == TextType.DEFINITION:
            return self.DEFINITIONS.get(self.text, "")
        return ""

    def render(self):
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
        self.interpretable = self.text_type == TextType.NORMAL and self.clean_text in self.ENTRIES
        self.definable = self.text_type == TextType.INDEX and self.clean_text in self.INDICES
        self.definition = self.text_type == TextType.DEFINITION and self.clean_text in self.DEFINITIONS

    def highlight(self):
        if self.text_type == TextType.INDEX and not self.selected:
            self.selected = True
            self.size += 6
            self.render()

    def restore(self):
        if self.text_type == TextType.INDEX and self.selected:
            self.selected = False
            self.size -= 6
            self.render()

    def update(self, update_type):
        if update_type in [1, 2] and self.text_type in [TextType.DEFINITION, TextType.INDEX]:
            self.selected = False
            self.render()

    @staticmethod
    def clean_word(word):
        return word.strip(".,()¿?¡!")
