#!/usr/bin/env python

import re

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


# Maps legacy string names (still used by Text/InlineText callers) to enum members.
_TEXT_TYPE_NAMES: dict = {
    "normal": TextType.NORMAL,
    "active_text": TextType.ACTIVE,
    "intercalado": TextType.INTERCALATED,
    "instruccion": TextType.INSTRUCTION,
    "indice": TextType.INDEX,
    "definicion": TextType.DEFINITION,
    "concepto": TextType.CONCEPT,
    "textbox": TextType.TEXT_BOX,
}

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
        @param text_type: Rendering role; accepts a TextType member, its integer value, or a string name from _TEXT_TYPE_NAMES.
        @type text_type: TextType | int | str
        @param font_manager: Font cache used to obtain the correct typeface.
        @type font_manager: FontManager
        """
        super().__init__()
        self.text = text
        self.size = size
        if isinstance(text_type, str):
            self.text_type = _TEXT_TYPE_NAMES.get(text_type, TextType.NORMAL)
        elif isinstance(text_type, TextType):
            self.text_type = text_type
        else:
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

        effective_size = (
            self.size + 6
            if self.text_type == TextType.INDEX and self.selected
            else self.size
        )
        font = self.font_manager.get_font(effective_size, bold, underline)

        if self.text_type == TextType.INDEX:
            color = (122, 140, 31) if self.clean_text in self.INDICES else (60, 36, 21)
        else:
            color = (0, 0, 0) if self.text_type in [TextType.NORMAL, TextType.ACTIVE, TextType.INTERCALATED, TextType.INSTRUCTION] else (60, 36, 21)

        self.image = font.render(self.text, True, color)
        new_rect = self.image.get_rect()
        if hasattr(self, "rect"):
            new_rect.topleft = self.rect.topleft
        self.rect = new_rect

        self.update_flags()

    def update_flags(self):
        """Recompute interpretable, definable, and definition flags from the current state."""
        self.interpretable = self.text_type == TextType.NORMAL and self.clean_text in self.ENTRIES
        self.definable = self.text_type == TextType.INDEX and self.clean_text in self.INDICES
        self.definition = self.text_type == TextType.DEFINITION and self.clean_text in self.DEFINITIONS

    def highlight(self):
        """Select and enlarge this word if it is an INDEX type and not already selected."""
        if self.text_type == TextType.INDEX and not self.selected:
            self.selected = True
            self.render()

    def restore(self):
        """Deselect and shrink this word if it is an INDEX type and currently selected."""
        if self.text_type == TextType.INDEX and self.selected:
            self.selected = False
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


def _tokenize(text, size, text_type, space_px=6):
    """
    Split *text* into Word sprites.

    Uses ``re.split(r'(\\s+)', text.strip())`` so every token (including the last word of a
    line that does not end with a space) is captured.  The alternating split result gives
    word tokens at even indices and whitespace runs at odd indices; the whitespace run
    immediately before each word is used to scale the gap between words, allowing
    multi-space alignment strings like ``"Sí            No"`` to render with proportional spacing.

    @param text: Text string to tokenize.
    @type text: str
    @param size: Font size passed to each Word.
    @type size: int
    @param text_type: Text type passed to each Word (string name, int value, or TextType member).
    @param space_px: Pixel width of a single space character; used to scale inter-word gaps.
    @type space_px: int
    @return: Tuple of ``(words, word_gaps)`` where ``word_gaps[i]`` is the pixel gap to
             insert before ``words[i]`` (0 for the first word).
    @rtype: tuple[list[Word], list[int]]
    """
    words: list = []
    word_gaps: list = []
    tokens = re.split(r"(\s+)", text.strip())
    for i, token in enumerate(tokens):
        if not token:
            continue
        if i % 2 == 0:  # even index → word token; odd index → whitespace run
            words.append(Word(token, size, text_type))
            if not word_gaps:
                word_gaps.append(0)  # no gap before the first word
            else:
                spaces_tok = tokens[i - 1] if i >= 1 else ""
                n = len(spaces_tok)
                # Single space → use space_px minimum; longer runs → scale up.
                word_gaps.append(max(space_px, n * space_px))
    return words, word_gaps


class TextLayout:
    """Mixin providing the shared word-wrap-and-position utility.

    Subclasses must ensure ``self.left_limit`` and ``self.right_limit`` are set
    before calling ``_wrap_and_position``.

    ``Text`` uses ``_wrap_and_position`` directly in ``_layout_words``.
    ``InlineText`` inherits the mixin but keeps its own positioning loop because
    its requirements differ: justified inter-word spacing (per-line ``medidas``),
    vertical centring of words within uniform line heights, and ``|`` hard-break
    tokens.  ``_wrap_and_position`` remains available to ``InlineText`` as the
    algorithm converges in the future.
    """

    def _wrap_and_position(self, words, gaps, start_x, start_y):
        """Place word sprites left-to-right, wrapping at ``self.right_limit``.

        ``gaps[i]`` is the pixel gap to insert *before* word *i*; it is always
        forced to 0 at the start of a new line.  Directly sets
        ``word.rect.topleft`` for every word.

        @param words: Ordered sequence of Word sprites to lay out.
        @type words: list[Word]
        @param gaps: Per-word gap in pixels (same length as *words*; gaps[0] is ignored).
        @type gaps: list[int]
        @param start_x: Left edge of the first line (pixels).
        @type start_x: int | float
        @param start_y: Top edge of the first line (pixels).
        @type start_y: int | float
        @return: ``(max_width, total_height)`` of the laid-out block.
        @rtype: tuple[int | float, int | float]
        """
        if not words:
            return 0, 0
        x = start_x
        y = start_y
        max_width = 0
        total_height = 0
        at_line_start = True

        for idx, word in enumerate(words):
            gap = 0 if at_line_start else gaps[idx]
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

        return max_width, total_height + words[-1].rect.height
