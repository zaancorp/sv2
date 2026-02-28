#!/usr/bin/env python

import pygame

from .palabra import palabra

# ---------------------------------------------------------------------------
# Layout constants for the 1024×572 display
# ---------------------------------------------------------------------------

# Horizontal bounds used when estimating how many lines a text block spans.
# The estimate pass walks left→right across a virtual 1024-px line using these
# values; the actual layout margins are then chosen from the table below.
_MEASURE_LEFT  = 128
_MEASURE_RIGHT = 896   # = 1024 - _MEASURE_LEFT

# Left/right layout margins for auto-layout mode (custom=False), chosen by the
# estimated line count.  Values are (left_margin, right_margin).
_LAYOUT_1LINE = (256, 768)
_LAYOUT_2LINE = (192, 832)
_LAYOUT_3PLUS = (32,  992)

# Vertical centre of the text-box panel that appears in content screens.
# The panel image is placed at y=332; this constant is the pixel row used to
# vertically centre a text block within that panel area.
_TEXT_AREA_VCENTER = 382


class Text:
    def __init__(self, x, y, text, size, text_type, right_limit, custom=True):
        self.x = x
        self.y = y
        self.text_type = text_type
        self.words = []
        self.space = 6
        self.line_number = 0

        for word in text.split():
            if word.lower() != "reproducción" or text_type == "texto_act":
                self.words.append(palabra(word, size, text_type))

        self.left_limit, self.right_limit = self._calculate_limits(custom, right_limit)
        self.total_width, self.total_height = self._layout_words()

        self.rect = pygame.Rect(x, y, self.total_width, self.total_height)

    def _calculate_limits(self, custom, right_limit):
        if custom:
            return self.x, right_limit
        elif self.text_type == "instruccion":
            return self.x, right_limit
        else:
            line_count = self._estimate_line_count()
            if line_count == 1:
                return _LAYOUT_1LINE
            elif line_count == 2:
                return _LAYOUT_2LINE
            else:
                return _LAYOUT_3PLUS

    def _estimate_line_count(self):
        x = _MEASURE_LEFT
        line_count = 1
        for word in self.words:
            if x + word.rect.width > _MEASURE_RIGHT:
                x = _MEASURE_LEFT
                line_count += 1
            x += word.rect.width + self.space
        return line_count

    def _layout_words(self):
        x = self.left_limit
        y = self.y if self.text_type == "instruccion" else _TEXT_AREA_VCENTER - (self._estimate_total_height() / 2)
        max_width = 0
        total_height = 0

        for word in self.words:
            if x + word.rect.width > self.right_limit:
                x = self.left_limit
                y += word.rect.height
                total_height += word.rect.height
            word.rect.topleft = (x, y)
            x += word.rect.width + self.space
            max_width = max(max_width, x - self.left_limit)

        return max_width, total_height + word.rect.height

    def _estimate_total_height(self):
        return self.words[0].rect.height * self._estimate_line_count()

    def indexar(self, letter):
        if self.text_type == "indice":
            for word in self.words:
                if letter == word.palabra.strip():
                    word.selec = True
                    word.destacar()
                else:
                    word.restaurar()
