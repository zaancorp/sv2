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

    def load_texts(self):
        """Build text objects for the instruction label and all three audience sections."""
        self.speech_server.processtext(
            "Pantalla: Orientaciones y Sugerencias: "
            "Pulsa sobre cada botón para que puedas explorar las orientaciones y sugerencias. ",
            self.parent.config.is_screen_reader_enabled(),
        )
        self.texto11 = Text(
            400,
            200,
            self.screen_text("text_1"),
            self.parent.config.get_font_size(),
            "instruccion",
            800,
        )
        self.texto11_5_1 = Text(
            300,
            130,
            self.screen_text("text_5_1"),
            self.parent.config.get_font_size(),
            1,
            900,
        )
        self.texto11_5_2 = Text(
            300,
            self.texto11_5_1.y + self.texto11_5_1.final_width + 10,
            self.screen_text("text_5_2"),
            self.parent.config.get_font_size(),
            1,
            900,
        )
        self.texto11_5_3 = Text(
            300,
            self.texto11_5_2.y + self.texto11_5_2.final_width + 10,
            self.screen_text("text_5_3"),
            self.parent.config.get_font_size(),
            1,
            900,
        )
        self.texto11_6_1 = Text(
            300,
            130,
            self.screen_text("text_6_1"),
            self.parent.config.get_font_size(),
            1,
            900,
        )
        self.texto11_6_2 = Text(
            300,
            self.texto11_6_1.y + self.texto11_6_1.final_width + 10,
            self.screen_text("text_6_2"),
            self.parent.config.get_font_size(),
            1,
            900,
        )
        self.texto11_6_3 = Text(
            300,
            self.texto11_6_2.y + self.texto11_6_2.final_width + 10,
            self.screen_text("text_6_3"),
            self.parent.config.get_font_size(),
            1,
            900,
        )
        self.texto11_7_1 = Text(
            300,
            130,
            self.screen_text("text_7_1"),
            self.parent.config.get_font_size(),
            1,
            900,
        )
        self.texto11_7_2 = Text(
            300,
            self.texto11_7_1.y + self.texto11_7_1.final_width + 10,
            self.screen_text("text_7_2"),
            self.parent.config.get_font_size(),
            1,
            900,
        )
        self.texto11_7_3 = Text(
            300,
            self.texto11_7_2.y + self.texto11_7_2.final_width + 10,
            self.screen_text("text_7_3"),
            self.parent.config.get_font_size(),
            1,
            900,
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

            if event.type == pygame.KEYDOWN:

                self.collect_buttons(self.button_group)
                self.nav_list = self.button_list
                self.element_count = len(self.nav_list)

                if event.key == pygame.K_ESCAPE:
                    self.clear_groups()
                    self.parent.popState()
                elif event.key == pygame.K_LEFT:
                    self.nav_left()

                elif event.key == pygame.K_RIGHT:
                    self.nav_right()

                elif event.key == pygame.K_RETURN:
                    self.focus_index = -1
                    if self.x.obj_type == "button":
                        if self.x.id == "or-ninos":
                            self.word_group.empty()
                            self.banner_group.empty()
                            self.word_group.add(
                                self.texto11_5_1.words,
                                self.texto11_5_2.words,
                                self.texto11_5_3.words,
                            )
                            self.caja_or.resize(
                                height=self.texto11_5_1.final_width
                                + self.texto11_5_2.final_width
                                + self.texto11_5_3.final_width
                                + 30
                            )
                            self.banner_group.add(
                                self.banner_or_es, self.caja_or, self.banner_inf
                            )
                            self.speech_server.processtext(
                                self.screen_text("text_5_1l")
                                + self.screen_text("text_5_2l")
                                + self.screen_text("text_5_3l")
                                + "Ahora, utiliza las teclas de dirección y explora la siguiente orientación o sugerencia. ",
                                self.parent.config.is_screen_reader_enabled(),
                            )

                        elif self.x.id == "or-docentes":
                            self.word_group.empty()
                            self.banner_group.empty()
                            self.word_group.add(
                                self.texto11_6_1.words,
                                self.texto11_6_2.words,
                                self.texto11_6_3.words,
                            )
                            self.caja_or.resize(
                                height=self.texto11_6_1.final_width
                                + self.texto11_6_2.final_width
                                + self.texto11_6_3.final_width
                                + 30
                            )
                            self.banner_group.add(
                                self.banner_or_doc, self.caja_or, self.banner_inf
                            )

                            self.speech_server.processtext(
                                self.screen_text("text_6_1l")
                                + self.screen_text("text_6_2l")
                                + self.screen_text("text_6_3l")
                                + "Ahora, utiliza las teclas de dirección y explora la siguiente orientación o sugerencia. ",
                                self.parent.config.is_screen_reader_enabled(),
                            )

                        elif self.x.id == "or-padres":
                            self.word_group.empty()
                            self.banner_group.empty()
                            self.word_group.add(
                                self.texto11_7_1.words,
                                self.texto11_7_2.words,
                                self.texto11_7_3.words,
                            )
                            self.caja_or.resize(
                                height=self.texto11_7_1.final_width
                                + self.texto11_7_2.final_width
                                + self.texto11_7_3.final_width
                                + 30
                            )
                            self.banner_group.add(
                                self.banner_or_pa, self.caja_or, self.banner_inf
                            )

                            self.speech_server.processtext(
                                self.screen_text("text_7_1l")
                                + self.screen_text("text_7_2l")
                                + self.screen_text("text_7_3l")
                                + "Fin de contenido, regresa al menú. ",
                                self.parent.config.is_screen_reader_enabled(),
                            )

                        elif self.x.id == "puerta":
                            self.clear_groups()
                            self.parent.popState()

            if pygame.sprite.spritecollideany(self.mouse, self.button_group):
                sprite = pygame.sprite.spritecollide(
                    self.mouse, self.button_group, False
                )
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if sprite[0].id == "puerta":
                        self.clear_groups()
                        self.parent.popState()

                    elif sprite[0].id == "audience-kids-btn":
                        self.word_group.empty()
                        self.banner_group.empty()
                        self.word_group.add(
                            self.texto11_5_1.words,
                            self.texto11_5_2.words,
                            self.texto11_5_3.words,
                        )
                        self.caja_or.resize(
                            height=self.texto11_5_1.final_width
                            + self.texto11_5_2.final_width
                            + self.texto11_5_3.final_width
                            + 30
                        )
                        self.banner_group.add(
                            self.banner_or_es, self.caja_or, self.banner_inf
                        )

                    elif sprite[0].id == "audience-teachers-btn":
                        self.word_group.empty()
                        self.banner_group.empty()
                        self.word_group.add(
                            self.texto11_6_1.words,
                            self.texto11_6_2.words,
                            self.texto11_6_3.words,
                        )
                        self.caja_or.resize(
                            height=self.texto11_6_1.final_width
                            + self.texto11_6_2.final_width
                            + self.texto11_6_3.final_width
                            + 30
                        )
                        self.banner_group.add(
                            self.banner_or_doc, self.caja_or, self.banner_inf
                        )

                    elif sprite[0].id == "audience-parents-btn":
                        self.word_group.empty()
                        self.banner_group.empty()
                        self.word_group.add(
                            self.texto11_7_1.words,
                            self.texto11_7_2.words,
                            self.texto11_7_3.words,
                        )
                        self.caja_or.resize(
                            height=self.texto11_7_1.final_width
                            + self.texto11_7_2.final_width
                            + self.texto11_7_3.final_width
                            + 30
                        )
                        self.banner_group.add(
                            self.banner_or_pa, self.caja_or, self.banner_inf
                        )
        self.handle_magnifier(events)

    def update(self):
        """Update cursor position, magnifier, and button tooltips."""
        self.mouse.update()
        self.magnifier.magnificar(self.parent.screen)
        self.button_group.update(self.tooltip_group)
