#!/usr/bin/env python

import pygame

from components import screen
from components.texto import Text
from paginas import pantalla2

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
        self.parent = parent
        # Calls Pantalla.__init__, which creates all per-screen sprite groups,
        # loads the background registered under "screen_gen", and resets navigation state.
        super().__init__(parent, self.name)
        self.is_overlay = is_overlay
        self.speech_server.processtext(
            self.parent.text_loader.ui("config_screens", "general", "title_reader"),
            False,
        )

        # --- Question label ---
        self.q1_label = Text(
            310,
            70,
            self.parent.text_loader.ui("config_screens", "general", "q1_language"),
            20,
            1,
            700,
        )
        # --- Option text label (sits below the toggle buttons) ---
        self.q1_options = Text(
            370,
            150,
            self.parent.text_loader.ui("config_screens", "general", "opt_languages"),
            20,
            1,
            700,
        )
        # --- Save hint ---
        self.save_hint_label = Text(
            200,
            400,
            self.parent.text_loader.ui("config_screens", "general", "save_hint"),
            20,
            1,
            800,
        )

        self.load_banners(banners)
        self.load_buttons(buttons)
        self._load_preferences()

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

    def handleEvents(self, events):
        """
        Evaluate events generated on this screen.

        @param events: Event list from the main loop.
        @type events: list
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.parent.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.clear_groups()
                    if self.is_overlay:
                        self.parent.RETURN_TO_PREV_SCREEN = True
                    self.parent.popState()

            if pygame.sprite.spritecollideany(self.mouse, self.button_group):
                sprite = pygame.sprite.spritecollide(
                    self.mouse, self.button_group, False
                )
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    if sprite[0].id == "puerta":
                        self.clear_groups()
                        self.parent.popState()

                    elif sprite[0].id == "lang_es":
                        # Switch selection: ES selected, HU unselected
                        self.button_group.remove(self.lang_es, self.lang_hu_sel)
                        self.button_group.add(self.lang_es_sel, self.lang_hu)
                        self.parent.config.set_language("es")

                    elif sprite[0].id == "lang_hu":
                        # Switch selection: HU selected, ES unselected
                        self.button_group.remove(self.lang_es_sel, self.lang_hu)
                        self.button_group.add(self.lang_es, self.lang_hu_sel)
                        self.parent.config.set_language("hu")

                    elif sprite[0].id == "guardar":
                        self.parent.config.set_preference("cache", True)
                        self.parent.config.flush()
                        self.parent.reload_text_content()
                        self.clear_groups()
                        if self.parent.first_run:
                            self.parent.changeState(pantalla2.Screen(self.parent))
                        else:
                            if self.is_overlay:
                                self.parent.RETURN_TO_PREV_SCREEN = True
                            self.parent.popState()

        self.handle_magnifier(events)

    def update(self):
        """
        Update the cursor position, screen magnifier, and button tooltips.
        """
        self.mouse.update()
        self.magnifier.magnificar(self.parent.screen)
        self.button_group.update(self.tooltip_group)
