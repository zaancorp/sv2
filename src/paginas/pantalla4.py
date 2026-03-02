#!/usr/bin/env python
"""Content screen covering the parts of a plant (screen 4)."""

import pygame

from components import screen
from components.image import Image

from paginas import menucfg
from paginas import pantalla2
from paginas import pantalla3
from paginas import pantalla10

animations = [
    "animation-4",
    "animation-4-1",
    "animation-4-2",
    "animation-4-3",
    "animation-4-4",
]

banners = [
    "banner-inf",
    "banner-partes",
]

buttons = [
    "home",
    "back",
    "config",
    "next",
]


class Screen(screen.Screen):
    """Screen presenting the parts of a plant through sequenced animations and rich text."""

    def __init__(self, parent):
        """
        Initialise the screen.

        @param parent: Screen manager instance.
        @type parent: Manejador
        """

        self.name = "screen_4"
        super().__init__(parent, self.name)

        self.load_animations(animations)
        self.load_banners(banners)
        self.load_buttons(buttons)
        self.load_texts()

        # Add to the banners group

        self.caja_texto = Image(0, 332, self.backgrounds_path + "caja-texto.png")

        self.update_group.add(
            self.animation_4,
            self.animation_4_1,
            self.animation_4_2,
            self.animation_4_3,
            self.animation_4_4,
        )

    def load_texts(self):
        """Load and build the text objects used on this screen."""
        texts = self.load_screen_texts(
            ["text_2", "text_3", "text_4", "text_5"], x=64, right_limit=960
        )
        self.texto4_2 = texts["text_2"]
        self.texto4_3 = texts["text_3"]
        self.texto4_4 = texts["text_4"]
        self.texto4_5 = texts["text_5"]

    def start(self):
        self.resume()

    def resume(self):
        """Reload buttons and texts if config changed, then initialise sprite groups and start the first animation step."""
        if self.parent.config.is_text_change_enabled():
            self.load_buttons(buttons)
            self.load_texts()
            self.parent.config.set_text_change_enabled(False)
        self.banner_group.add(self.banner_partes, self.banner_inf)
        self.anim_group.add(self.animation_4)
        self.button_group.add(self.config, self.back, self.next, self.home)
        self.creado = True
        self.elapsed_ms = 0
        self.animation_4.detener()
        if self.current_anim == 0:
            self.current_anim = 1
        self.speech_server.processtext(
            "Pantalla: Partes de una planta", self.parent.config.is_screen_reader_enabled()
        )
        self.reproducir_animacion(self.current_anim)

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
                self.nav_list = self.word_list + self.button_list
                self.element_count = len(self.nav_list)

                if event.key == pygame.K_RIGHT:
                    self.keyboard_nav_active = True
                    self.nav_right()

                elif event.key == pygame.K_LEFT:
                    self.nav_left()
                    self.keyboard_nav_active = True

                elif self.keyboard_nav_active:
                    if event.key == pygame.K_RETURN:
                        if self.x.obj_type == "button":
                            self.keyboard_nav_active = False
                            if self.x.id == "next":
                                if self.current_anim <= 7:
                                    self.current_anim += 1
                                    self.reproducir_animacion(self.current_anim)

                            elif self.x.id == "back":
                                self.current_anim -= 1
                                self.reproducir_animacion(self.current_anim)
                                if self.current_anim == 1:
                                    self.update_group.update()
                                    self.clear_groups()
                                    self.resume()

                            elif self.x.id == "config":
                                self.clear_groups()
                                self.parent.pushState(
                                    menucfg.Screen(self.parent, self.is_overlay)
                                )

                            elif self.x.id == "home":
                                self.clear_groups()
                                self.parent.changeState(pantalla2.Screen(self.parent))

                        elif self.x.obj_type == "word":
                            self.keyboard_nav_active = False
                            self.speech_server.processtext(
                                self.parent.text_loader.concept(self.x.codigo),
                                self.parent.config.is_screen_reader_enabled(),
                            )

            if pygame.sprite.spritecollideany(self.mouse, self.word_group):
                sprite = pygame.sprite.spritecollide(
                    self.mouse, self.word_group, False
                )
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if sprite[0].obj_type == "word":
                        if sprite[0].interpretable == True:
                            self.parent.show_concept(sprite[0].codigo)

            if pygame.sprite.spritecollideany(self.mouse, self.button_group):
                sprite = pygame.sprite.spritecollide(
                    self.mouse, self.button_group, False
                )
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.speech_server.stopserver()
                    if sprite[0].id == "home":
                        self.clear_groups()
                        self.parent.changeState(pantalla2.Screen(self.parent))
                    elif sprite[0].id == "config":
                        self.clear_groups()
                        self.parent.pushState(menucfg.Screen(self.parent, self.is_overlay))
                    elif sprite[0].id == "repe":
                        self.update_group.update()
                        self.clear_groups()
                        self.resume()
                    elif sprite[0].id == "next":
                        self.keyboard_nav_active = False
                        if self.current_anim <= 7:
                            self.current_anim += 1
                            self.reproducir_animacion(self.current_anim)
                    elif sprite[0].id == "back":
                        self.keyboard_nav_active = False
                        self.current_anim -= 1
                        self.reproducir_animacion(self.current_anim)
                        if self.current_anim == 1:
                            self.update_group.update()
                            self.clear_groups()
                            self.resume()
        self.handle_magnifier(events)

    def update(self):
        """Update cursor position, magnifier, button tooltips, and trigger the first text display after the initial delay."""
        self.mouse.update()
        self.magnifier.magnificar(self.parent.screen)
        self.button_group.update(self.tooltip_group)
        if self.current_anim == 1 and not self.parent.config.is_screen_reader_enabled():
            if not self.elapsed_ms < 1000:
                self.text_bg_group.add(self.caja_texto)
                self.word_group.add(self.texto4_2.words)
                self.txt_actual = self.texto4_2.words
                self.collect_words(self.txt_actual)
                self.animation_4.continuar()

        self.elapsed_ms += self.frame_clock.get_time()

    def reproducir_animacion(self, animation_index):
        """
        Advance the screen to the given animation step, updating sprite groups and TTS accordingly.

        @param animation_index: Index of the animation step to display.
        @type animation_index: int
        """
        if animation_index <= 0:
            self.clear_groups()
            self.parent.changeState(pantalla3.Screen(self.parent))

        if animation_index == 1:
            self.focus_index = -1
            self.anim_group.remove(self.animation_4_1)
            self.word_group.empty()

            if self.parent.config.is_screen_reader_enabled():
                if self.first_entry:
                    self.speech_server.processtext2(
                        self.screen_text("text_2"),
                        self.parent.config.is_screen_reader_enabled(),
                    )
                    self.first_entry = False
                else:
                    self.speech_server.processtext(
                        self.screen_text("text_2"),
                        self.parent.config.is_screen_reader_enabled(),
                    )
                self.text_bg_group.add(self.caja_texto)
                self.word_group.add(self.texto4_2.words)
                self.txt_actual = self.texto4_2.words
                self.collect_words(self.txt_actual)
                self.animation_4.continuar()

        # Anim
        if animation_index == 2:
            self.focus_index = -1
            self.word_list = []
            self.word_group.empty()
            self.text_bg_group.empty()
            self.animation_4.detener()
            self.anim_group.add(self.animation_4_1)
            self.animation_4_1.update()
            self.animation_4_1.stop = False
            self.animation_4_1.continuar()
            self.speech_server.processtext(
                self.screen_text("anim_1"),
                self.parent.config.is_screen_reader_enabled(),
            )

        # Explicacion
        if animation_index == 3:
            self.focus_index = -1
            self.anim_group.empty()
            self.word_group.empty()
            self.anim_group.add(self.animation_4)
            self.animation_4.continuar()
            self.text_bg_group.add(self.caja_texto)
            self.word_group.add(self.texto4_3.words)
            self.txt_actual = self.texto4_3.words
            self.collect_words(self.txt_actual)
            self.speech_server.processtext(
                self.screen_text("text_3"),
                self.parent.config.is_screen_reader_enabled(),
            )

        # Anim
        if animation_index == 4:
            self.focus_index = -1
            self.word_list = []
            self.word_group.empty()
            self.text_bg_group.empty()
            self.animation_4.detener()
            self.anim_group.add(self.animation_4_2)
            self.animation_4_2.update()
            self.animation_4_2.stop = False
            self.animation_4_2.continuar()
            self.speech_server.processtext(
                self.screen_text("anim_2"),
                self.parent.config.is_screen_reader_enabled(),
            )

        # Explicacion
        if animation_index == 5:
            self.focus_index = -1
            self.anim_group.empty()
            self.word_group.empty()
            self.anim_group.add(self.animation_4)
            self.animation_4.continuar()
            self.text_bg_group.add(self.caja_texto)
            self.word_group.add(self.texto4_4.words)
            self.txt_actual = self.texto4_4.words
            self.collect_words(self.txt_actual)
            self.speech_server.processtext(
                self.screen_text("text_4"),
                self.parent.config.is_screen_reader_enabled(),
            )

        # Anim
        if animation_index == 6:
            self.focus_index = -1
            self.word_list = []
            self.word_group.empty()
            self.text_bg_group.empty()
            self.animation_4.detener()
            self.anim_group.add(self.animation_4_3)
            self.animation_4_3.update()
            self.animation_4_3.stop = False
            self.animation_4_3.continuar()
            self.speech_server.processtext(
                self.screen_text("anim_3"),
                self.parent.config.is_screen_reader_enabled(),
            )

        # Explicacion
        if animation_index == 7:
            self.focus_index = -1
            self.anim_group.empty()
            self.word_group.empty()
            self.anim_group.add(self.animation_4)
            self.animation_4.continuar()
            self.text_bg_group.add(self.caja_texto)
            self.button_group.add(self.next)
            self.word_group.add(self.texto4_5.words)
            self.txt_actual = self.texto4_5.words
            self.collect_words(self.txt_actual)
            self.speech_server.processtext(
                self.screen_text("text_5"),
                self.parent.config.is_screen_reader_enabled(),
            )

        if animation_index == 8:
            self.focus_index = -1
            self.word_list = []
            self.tooltip_group.empty()
            self.word_group.empty()
            self.text_bg_group.empty()
            self.animation_4.detener()
            self.anim_group.add(self.animation_4_4)
            self.animation_4_4.update()
            self.animation_4_4.stop = False
            self.animation_4_4.continuar()
            self.button_group.remove(self.next)
            self.speech_server.processtext(
                self.screen_text("anim_4"),
                self.parent.config.is_screen_reader_enabled(),
            )

    def go_to_glossary(self):
        self.parent.pushState(pantalla10.Screen(self.parent))
