#!/usr/bin/env python
"""Glossary screen allowing students to look up plant biology concepts (screen 10)."""

import pygame

from components import screen
from components.texto import Text
from components.image import Image
from components.words import Word as _Word, font_manager as _font_manager


banners = [
    "banner-inf",
    "banner-glo",
]

buttons = ["home", "back"]


class Screen(screen.Screen):
    """Screen that presents a navigable alphabetical glossary of plant biology terms."""

    def __init__(self, parent):
        """
        Initialise the glossary screen and display the entry for the last-viewed concept.

        @param parent: Screen manager instance.
        @type parent: Manejador
        """

        self.name = "screen_10"
        super().__init__(parent, self.name)

        self.is_overlay = False

        self.caja_concepto = Image(590, 190, self.misc_path + "caja-concepto.png")

        self.load_banners(banners)
        self.load_texts()
        self.load_buttons(buttons)

        _def = self.parent.config.get_preference("definicion", "")
        inicial = self._find_initial(_def)
        self.abc.indexar(inicial)
        self.word_group.add(
            self.abc.words,
            self.indices(inicial, _def),
            self.mostrar_concepto(_def),
        )
        self.caja_concepto.resize(height=self.concepto.total_height)
        self.banner_group.add(self.banner_glo, self.caja_concepto, self.banner_inf)
        self.button_group.add(self.back, self.home)

    def load_texts(self):
        """Build the alphabet index, concept display, and glossary entry sprites from active language data."""
        # Alphabet row: only the letters that have entries in the active language.
        abc_text = "  ".join(_Word.INDICES) + " "
        self.abc = Text(290, 140, abc_text, 18, "indice", 1010)

        # Placeholder for the definition text shown on the right.
        self.concepto = Text(
            600, 200, "", self.parent.config.get_font_size(), "concepto", 1000
        )

        # Group DEFINITIONS labels by their INDICES prefix.
        # Sort by length descending so digraphs like "Cs" are tried before "C".
        sorted_idx = sorted(_Word.INDICES, key=len, reverse=True)
        groups = {idx: [] for idx in _Word.INDICES}
        for label in sorted(_Word.DEFINITIONS):
            label_upper = label.upper()
            for idx in sorted_idx:
                if label_upper.startswith(idx.upper()):
                    groups[idx].append(label)
                    break

        # Create one Word sprite per entry. Using the full label as the Word text
        # means clean_text matches the DEFINITIONS key even for multi-word phrases
        # ("Reproducción asexual"), giving the correct .code and .definition flag.
        BASE_Y, Y_STEP = 200, 50
        self._entry_words: dict[str, list[_Word]] = {}
        for idx in _Word.INDICES:
            sprites = []
            for pos, label in enumerate(groups[idx]):
                w = _Word(label, 22, "definicion", _font_manager)
                w.rect.topleft = (330, BASE_Y + pos * Y_STEP)
                sprites.append(w)
            self._entry_words[idx] = sprites

    def _find_initial(self, code):
        """Return the INDICES letter whose entry bucket contains the given concept code.

        @param code: Concept code to look up (e.g. ``"absorber"``).
        @type code: str
        @return: The matching INDICES letter, or an empty string if not found.
        @rtype: str
        """
        for idx, words in self._entry_words.items():
            for word in words:
                if word.code == code:
                    return idx
        return ""

    def handleEvents(self, events):
        """
        Process input events for this screen.

        @param events: Event list from the main loop.
        @type events: list
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.parent.quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.go_home()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.sprite.spritecollideany(self.mouse, self.word_group):
                    sprite = pygame.sprite.spritecollide(self.mouse, self.word_group, False)
                    if sprite[0].definable == True:
                        self.abc.indexar(sprite[0].text)
                        self.word_group.update(1)
                        sprite[0].selected = True
                        sprite[0].highlight()
                        self.word_group.empty()
                        self.banner_group.remove(self.caja_concepto)
                        self.word_group.add(
                            self.abc.words, self.indices(sprite[0].text)
                        )
                    elif sprite[0].definition == True:
                        self.word_group.update(2)
                        sprite[0].selected = True
                        self.banner_group.add(self.caja_concepto)
                        self.word_group.remove(self.concepto.words)
                        self.word_group.add(self.mostrar_concepto(sprite[0].code))
                        self.caja_concepto.resize(height=self.concepto.total_height)
                elif pygame.sprite.spritecollideany(self.mouse, self.button_group):
                    sprite = pygame.sprite.spritecollide(self.mouse, self.button_group, False)
                    if sprite[0].id == "home":
                        self.go_home()
                    elif sprite[0].id == "back":
                        self.clear_groups()
                        self.parent.popState()
        self.handle_magnifier(events)

    def mostrar_concepto(self, palabra):
        """
        Build a Text object for the given glossary term and return its word sprites.

        @param palabra: Glossary term key used to look up the concept text.
        @type palabra: str
        @return: Word sprites for the concept definition.
        @rtype: list
        """

        self.concepto = Text(
            600,
            200,
            self.parent.text_loader.concept(palabra),
            self.parent.config.get_font_size(),
            "concepto",
            1000,
        )
        return self.concepto.words

    def indices(self, valor, palabra_negrita=""):
        """
        Return entry Word sprites for the given index letter, marking the selected concept.

        @param valor: INDICES letter identifying the bucket (e.g. ``"A"``, ``"Cs"``).
        @type valor: str
        @param palabra_negrita: Concept code of the entry to mark as selected; empty for none.
        @type palabra_negrita: str
        @return: Word sprites for the matching entries.
        @rtype: list
        """
        palabras = []
        for word in self._entry_words.get(valor, []):
            word.selected = word.code == palabra_negrita
            word.render()
            palabras.append(word)
        return palabras
