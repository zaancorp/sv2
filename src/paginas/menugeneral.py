#!/usr/bin/env python

import pygame

from components import screen
from components.texto import Text

banners = [
    "banner-inf",
    "banner-acc-visual",
]

buttons = [
    "puerta",
    "guardar",
    "lang_es",
    "lang_es_sel",
    "lang_hu",
    "lang_hu_sel",
]


class Screen(screen.Screen):
    """General settings configuration screen for selecting the interface language."""

    def __init__(self, parent, is_overlay=False):
        """
        Initialiser for the general settings screen.

        @param parent: The screen manager instance.
        @type parent: Manejador
        @param is_overlay: True if this screen is stacked over another (pushed), False if loaded
        via changeState.
        @type is_overlay: bool
        """
        self.name = "screen_gen"
        # Calls Pantalla.__init__, which creates all per-screen sprite groups,
        # loads the background registered under "screen_gen", and resets navigation state.
        super().__init__(parent, self.name)
        self.is_overlay = is_overlay
        self.speech_server.processtext(
            self.parent.text_loader.ui("config_screens", "general", "title_reader"),
            False,
        )

        self.q1_label        = self._label(310, 70,  "q1_language")
        self.q1_options      = self._label(370, 150, "opt_languages")
        self.save_hint_label = self._label(200, 400, "save_hint",  right=800)

        self.load_banners(banners)
        self.load_buttons(buttons)
        self._load_preferences()
        self.button_actions = {
            "puerta":  lambda: (self.clear_groups(), self.parent.popState()),
            "lang_es": lambda: self._select_language("es"),
            "lang_hu": lambda: self._select_language("hu"),
            "guardar": self._save_and_exit,
        }

    def _label(self, x, y, key, right=700):
        """Create a config-screen Text label with standard size=20, text_type=1."""
        return Text(x, y, self.parent.text_loader.ui("config_screens", "general", key), 20, 1, right)

    def _select_language(self, lang):
        """Select the interface language; swaps all four lang buttons."""
        lang_map = {
            "es": (self.lang_es_sel, self.lang_hu),
            "hu": (self.lang_es,     self.lang_hu_sel),
        }
        self.button_group.remove(
            self.lang_es, self.lang_es_sel, self.lang_hu, self.lang_hu_sel
        )
        self.button_group.add(*lang_map[lang])
        self.parent.config.set_language(lang)

    def _load_preferences(self):
        """Populate sprite groups to reflect the currently saved language preference."""
        self.word_group.add(self.q1_label.words, self.q1_options.words)
        self.banner_group.add(self.banner_acc_visual, self.banner_inf)
        self.button_group.add(self.puerta)

        if self.parent.config.get_language() == "hu":
            self.button_group.add(self.lang_es, self.lang_hu_sel, self.guardar)
        else:
            # Default: Spanish selected
            self.button_group.add(self.lang_es_sel, self.lang_hu, self.guardar)

        self.word_group.add(self.save_hint_label.words)

    def _save_and_exit(self):
        """Persist the current preferences and return to the previous or main screen."""
        self.parent.config.set_preference("cache", True)
        self.parent.config.flush()
        self.parent.reload_text_content()
        self.parent.finish_config(self)

    def handleEvents(self, events):
        """
        Evaluate events generated on this screen.

        @param events: Event list from the main loop.
        @type events: list
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.parent.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.clear_groups()
                    if self.is_overlay:
                        self.parent.RETURN_TO_PREV_SCREEN = True
                    self.parent.popState()
            elif pygame.sprite.spritecollideany(self.mouse, self.button_group):
                sprite = pygame.sprite.spritecollide(self.mouse, self.button_group, False)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.button_actions.get(sprite[0].id, lambda: None)()
        self.handle_magnifier(events)
