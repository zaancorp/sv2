#!/usr/bin/env python
"""Orientations and suggestions screen for students, teachers, and parents (screen 11)."""

import pygame

from components import screen
from components.texto import Text
from components.image import Image

banners = [
    "banner-inf",
    "banner-or",
    "banner-or-es",
    "banner-or-pa",
    "banner-or-doc",
]

buttons = [
    "audience-kids-btn",
    "audience-teachers-btn",
    "audience-parents-btn",
    "puerta",
]

# Maps each audience button ID to the text keys, TTS keys, banner attribute name,
# and the trailing TTS sentence used after reading all three texts.
_AUDIENCES = {
    "audience-kids-btn": {
        "text_keys": ["text_5_1", "text_5_2", "text_5_3"],
        "speech_keys": ["text_5_1l", "text_5_2l", "text_5_3l"],
        "banner": "banner_or_es",
        "speech_suffix": "Ahora, utiliza las teclas de dirección y explora la siguiente orientación o sugerencia. ",
    },
    "audience-teachers-btn": {
        "text_keys": ["text_6_1", "text_6_2", "text_6_3"],
        "speech_keys": ["text_6_1l", "text_6_2l", "text_6_3l"],
        "banner": "banner_or_doc",
        "speech_suffix": "Ahora, utiliza las teclas de dirección y explora la siguiente orientación o sugerencia. ",
    },
    "audience-parents-btn": {
        "text_keys": ["text_7_1", "text_7_2", "text_7_3"],
        "speech_keys": ["text_7_1l", "text_7_2l", "text_7_3l"],
        "banner": "banner_or_pa",
        "speech_suffix": "Fin de contenido, regresa al menú. ",
    },
}


class Screen(screen.Screen):
    """Screen presenting usage orientations and suggestions for students, teachers, and parents."""

    def __init__(self, parent):
        """
        Initialise the screen.

        @param parent: Screen manager instance.
        @type parent: Manejador
        """

        self.name = "screen_11"
        super().__init__(parent, self.name)

        self.is_overlay = False

        # Banners

        self.caja_or = Image(290, 125, self.backgrounds_path + "caja.png")

        self.load_banners(banners)
        self.load_buttons(buttons)
        self.load_texts()

        self.word_group.add(self.texto11.words)
        self.banner_group.add(self.banner_or, self.banner_inf)
        self.button_group.add(
            self.audience_kids_btn,
            self.audience_teachers_btn,
            self.audience_parents_btn,
            self.puerta,
        )

        self.button_actions = {
            "puerta":                self._go_back,
            "audience-kids-btn":     lambda: self._show_audience("audience-kids-btn"),
            "audience-teachers-btn": lambda: self._show_audience("audience-teachers-btn"),
            "audience-parents-btn":  lambda: self._show_audience("audience-parents-btn"),
        }

    def load_texts(self):
        """Build text objects for the instruction label and all three audience sections."""
        self.speech_server.processtext(
            "Pantalla: Orientaciones y Sugerencias: "
            "Pulsa sobre cada botón para que puedas explorar las orientaciones y sugerencias. ",
            self.parent.config.is_screen_reader_enabled(),
        )
        font_size = self.parent.config.get_font_size()
        self.texto11 = Text(400, 200, self.screen_text("text_1"), font_size, "instruccion", 800)

        # Build three Text objects per audience group, chaining y positions.
        # Results stored as self._audience_texts[btn_id] = [Text, Text, Text].
        self._audience_texts = {}
        for btn_id, cfg in _AUDIENCES.items():
            texts = []
            y = 130
            for key in cfg["text_keys"]:
                t = Text(300, y, self.screen_text(key), font_size, 1, 900)
                texts.append(t)
                y = t.y + t.total_width + 10
            self._audience_texts[btn_id] = texts

    def _go_back(self):
        """Close this overlay and return to the previous screen."""
        self.clear_groups()
        self.parent.popState()

    def _show_audience(self, button_id):
        """
        Display the texts and banner for one audience group.

        Empties the current word and banner groups, adds the three Text objects
        for *button_id*, resizes the content box, shows the matching banner, and
        triggers the TTS read-out if the screen reader is active.

        @param button_id: One of the keys in ``_AUDIENCES``.
        @type button_id: str
        """
        cfg = _AUDIENCES[button_id]
        texts = self._audience_texts[button_id]
        self.word_group.empty()
        self.banner_group.empty()
        self.word_group.add(*(t.words for t in texts))
        self.caja_or.resize(height=sum(t.total_width for t in texts) + 30)
        self.banner_group.add(getattr(self, cfg["banner"]), self.caja_or, self.banner_inf)
        self.speech_server.processtext(
            "".join(self.screen_text(k) for k in cfg["speech_keys"]) + cfg["speech_suffix"],
            self.parent.config.is_screen_reader_enabled(),
        )

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
                    self._go_back()
                elif event.key == pygame.K_LEFT:
                    self.keyboard_nav_active = True
                    self.nav_left()
                elif event.key == pygame.K_RIGHT:
                    self.keyboard_nav_active = True
                    self.nav_right()
                elif self.keyboard_nav_active and event.key == pygame.K_RETURN:
                    self.keyboard_nav_active = False
                    if self.x.obj_type == "button":
                        self.button_actions.get(self.x.id, lambda: None)()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.sprite.spritecollideany(self.mouse, self.button_group):
                    sprite = pygame.sprite.spritecollide(self.mouse, self.button_group, False)
                    self.button_actions.get(sprite[0].id, lambda: None)()

        self._rebuild_nav()
        self.handle_magnifier(events)
