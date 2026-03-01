#!/usr/bin/env python

import pygame

from librerias import pantalla
from librerias.texto import Text
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


class estado(pantalla.Pantalla):
    def __init__(self, parent, previa=False):
        """
        Initialiser for the general settings screen.

        @param parent: The screen manager instance.
        @type parent: Manejador
        @param previa: True if this screen is stacked over another (pushed), False if loaded
        via changeState.
        @type previa: bool
        """
        self.name = "screen_gen"
        self.parent = parent
        # Calls Pantalla.__init__, which creates all per-screen sprite groups,
        # loads the background registered under "screen_gen", and resets navigation state.
        super().__init__(parent, self.name)
        self.previa = previa
        self.spserver.processtext(
            self.parent.text_loader.ui("config_screens", "general", "title_reader"),
            False,
        )

        # --- Question label ---
        self.gen1_1 = Text(
            310,
            70,
            self.parent.text_loader.ui("config_screens", "general", "q1_language"),
            20,
            1,
            700,
        )
        # --- Option text label (sits below the toggle buttons) ---
        self.gen1_2 = Text(
            370,
            150,
            self.parent.text_loader.ui("config_screens", "general", "opt_languages"),
            20,
            1,
            700,
        )
        # --- Save hint ---
        self.gen1_3 = Text(
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
        self.grupo_palabras.add(self.gen1_1.words, self.gen1_2.words)
        self.grupo_banner.add(self.banner_acc_visual, self.banner_inf)
        self.grupo_botones.add(self.puerta)

        if self.parent.config.get_language() == "hu":
            self.grupo_botones.add(self.lang_es, self.lang_hu_sel, self.guardar)
        else:
            # Default: Spanish selected
            self.grupo_botones.add(self.lang_es_sel, self.lang_hu, self.guardar)

        self.grupo_palabras.add(self.gen1_3.words)

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
                    self.limpiar_grupos()
                    if self.previa:
                        self.parent.VOLVER_PANTALLA_PREVIA = True
                    self.parent.popState()

            if pygame.sprite.spritecollideany(self.raton, self.grupo_botones):
                sprite = pygame.sprite.spritecollide(
                    self.raton, self.grupo_botones, False
                )
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    if sprite[0].id == "puerta":
                        self.limpiar_grupos()
                        self.parent.popState()

                    elif sprite[0].id == "lang_es":
                        # Switch selection: ES selected, HU unselected
                        self.grupo_botones.remove(self.lang_es, self.lang_hu_sel)
                        self.grupo_botones.add(self.lang_es_sel, self.lang_hu)
                        self.parent.config.set_language("es")

                    elif sprite[0].id == "lang_hu":
                        # Switch selection: HU selected, ES unselected
                        self.grupo_botones.remove(self.lang_es_sel, self.lang_hu)
                        self.grupo_botones.add(self.lang_es, self.lang_hu_sel)
                        self.parent.config.set_language("hu")

                    elif sprite[0].id == "guardar":
                        self.parent.config.set_preference("cache", True)
                        self.parent.config.flush()
                        self.parent.reload_text_content()
                        self.limpiar_grupos()
                        if self.parent.primera_vez:
                            self.parent.changeState(pantalla2.estado(self.parent))
                        else:
                            if self.previa:
                                self.parent.VOLVER_PANTALLA_PREVIA = True
                            self.parent.popState()

        self.minimag(events)

    def update(self):
        """
        Update the cursor position, screen magnifier, and button tooltips.
        """
        self.raton.update()
        self.obj_magno.magnificar(self.parent.screen)
        self.grupo_botones.update(self.grupo_tooltip)
