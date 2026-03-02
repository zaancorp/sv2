#!/usr/bin/env python

import re
import pygame

from .words import Word, font_manager

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
        self.custom = custom
        self.words = []
        self.word_gaps = []   # pixel gap before each word (index 0 is always 0)
        self.space = 6
        self.line_number = 0

        # Measure the actual space-character pixel width for this font/size.
        # Used to honour multi-space runs like "Sí            No" in option labels.
        _font = font_manager.get_font(size)
        _space_px = max(1, _font.size(" ")[0])

        # Split preserving whitespace groups so that multi-space option-label
        # strings (e.g. "Sí            No") produce proportionally larger gaps.
        # re.split(r'(\s+)', s) returns alternating [word, spaces, word, …].
        tokens = re.split(r"(\s+)", text.strip())
        for i, token in enumerate(tokens):
            if not token:
                continue
            if i % 2 == 0:  # even index → word token
                if token.lower() != "reproducción" or text_type == "active_text":
                    self.words.append(Word(token, size, text_type))
                    if not self.word_gaps:
                        self.word_gaps.append(0)   # no gap before the first word
                    else:
                        # The spaces token immediately before this word is at i-1.
                        spaces_tok = tokens[i - 1] if i >= 1 else ""
                        n = len(spaces_tok)
                        # Single space → use self.space minimum; more → scale up.
                        self.word_gaps.append(max(self.space, n * _space_px))
            # Odd indices are whitespace tokens — consumed via tokens[i-1] above.

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
        y = (
            self.y
            if (self.text_type == "instruccion" or self.custom)
            else _TEXT_AREA_VCENTER - (self._estimate_total_height() / 2)
        )
        max_width = 0
        total_height = 0
        at_line_start = True

        for idx, word in enumerate(self.words):
            # Gap before this word: 0 at the start of each line, word_gaps[idx] otherwise.
            gap = 0 if at_line_start else self.word_gaps[idx]

            # Wrap to next line if (gap + word) would overflow the right margin.
            if not at_line_start and x + gap + word.rect.width > self.right_limit:
                x = self.left_limit
                y += word.rect.height
                total_height += word.rect.height
                gap = 0

            x += gap
            word.rect.topleft = (x, y)
            x += word.rect.width
            at_line_start = False
            max_width = max(max_width, x - self.left_limit)

        return max_width, total_height + word.rect.height

    def _estimate_total_height(self):
        return self.words[0].rect.height * self._estimate_line_count()

    def indexar(self, letter):
        if self.text_type == "indice":
            for word in self.words:
                if letter == word.text.strip():
                    word.selected = True
                    word.highlight()
                else:
                    word.restore()
