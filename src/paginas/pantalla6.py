#!/usr/bin/env python
"""Content screen covering plant reproduction (continued) and photosynthesis (screens 6–7)."""

import pygame

from components import screen
from components.image import Image

from paginas import menucfg
from paginas import pantalla2
from paginas import pantalla5
from paginas import pantalla10

animations = [
    "animation-6",
    "animation-6-2",
    "animation-6-3",
    "animation-6-4",
    "animation-6-5",
    "animation-6-6",
]

banners = [
    "banner-inf",
    "banner-repro",
]

buttons = [
    "home",
    "next",
    "back",
    "config",
]


class Screen(screen.Screen):
    """Screen presenting extended plant reproduction and photosynthesis content through sequenced animations."""

    def __init__(self, parent):
        """
        Initialise the screen.

        @param parent: Screen manager instance.
        @type parent: Manejador
        """

        self.name = "screen_6"
        super().__init__(parent, self.name)

        self.caja_texto = Image(0, 332, self.backgrounds_path + "caja-texto.png")

        self.load_animations(animations)
        self.load_banners(banners)
        self.load_buttons(buttons)
        self.load_texts()

    def load_texts(self):
        texts = self.load_screen_texts(
            ["text_2", "text_3", "text_4", "text_5", "text_6", "text_7", "text_8", "text_9"],
            x=32, right_limit=992
        )
        self.texto6_2 = texts["text_2"]
        self.texto6_3 = texts["text_3"]
        self.texto6_4 = texts["text_4"]
        self.texto7_2 = texts["text_5"]
        self.texto7_3 = texts["text_6"]
        self.texto7_4 = texts["text_7"]
        self.texto7_5 = texts["text_8"]
        self.texto7_6 = texts["text_9"]

    def start(self):
        self.resume()

    def resume(self):
        """Reload buttons and texts if config changed, then initialise sprite groups and start the current animation step."""
        if self.parent.config.is_text_change_enabled():
            self.load_buttons(buttons)
            self.load_texts()
            self.parent.config.set_text_change_enabled(False)
        self.anim_group.add(self.animation_6, self.animation_6_2)
        self.image_group.add(self.animation_6_2)
        self.banner_group.add(self.banner_repro, self.banner_inf)
        self.button_group.add(self.config, self.back, self.next, self.home)
        self.animation_6.detener()
        self.creado = True
        self.elapsed_ms = 0
        if self.current_anim == 0:
            self.current_anim = 1
        self.speech_server.stopserver()
        self.first_entry = True
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

                elif self.keyboard_nav_active:
                    if event.key == pygame.K_RETURN:
                        if self.x.obj_type == "button":
                            if self.x.id == "next":
                                self.repeticion = True
                                if self.current_anim <= 13:
                                    self.current_anim += 1
                                    self.reproducir_animacion(self.current_anim)
                                self.keyboard_nav_active = False

                            elif self.x.id == "back":
                                self.current_anim -= 1
                                self.reproducir_animacion(self.current_anim)
                                self.keyboard_nav_active = False

                            elif self.x.id == "config":
                                self.clear_groups()
                                self.parent.pushState(
                                    menucfg.Screen(self.parent, self.is_overlay)
                                )
                                self.keyboard_nav_active = False

                            elif self.x.id == "home":
                                self.clear_groups()
                                self.parent.changeState(pantalla2.Screen(self.parent))
                                self.keyboard_nav_active = False

                        elif self.x.obj_type == "word":
                            self.speech_server.processtext(
                                self.parent.text_loader.concept(self.x.codigo),
                                self.parent.config.is_screen_reader_enabled(),
                            )

            if pygame.sprite.spritecollideany(self.mouse, self.word_group):
                sprite = pygame.sprite.spritecollide(
                    self.mouse, self.word_group, False
                )
                if pygame.mouse.get_pressed() == (True, False, False):
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
                        # self.speech_server.stopserver()
                        self.clear_groups()
                        self.parent.changeState(pantalla2.Screen(self.parent))

                    elif sprite[0].id == "config":
                        self.clear_groups()
                        self.parent.pushState(menucfg.Screen(self.parent, self.is_overlay))

                    elif sprite[0].id == "next":
                        if self.current_anim <= 13:
                            self.current_anim += 1
                            self.reproducir_animacion(self.current_anim)
                    elif sprite[0].id == "back":
                        self.current_anim -= 1
                        self.reproducir_animacion(self.current_anim)
        self.handle_magnifier(events)

    def reproducir_animacion(self, animation_index):
        """
        Advance the screen to the given animation step, updating sprite groups and TTS accordingly.

        @param animation_index: Index of the animation step to display.
        @type animation_index: int
        """
        if animation_index <= 0:
            self.clear_groups()
            self.parent.animation_index = 10
            self.parent.changeState(pantalla5.Screen(self.parent, 9))
        elif animation_index == 1:
            self.focus_index = -1
            self.anim_group.remove(self.animation_6_3)

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

                self.anim_group.add(self.animation_6_2)
                self.text_bg_group.add(self.caja_texto)
                self.word_group.add(self.texto6_2.words)
                self.txt_actual = self.texto6_2.words
                self.collect_words(self.txt_actual)
                self.animation_6.continuar()

        elif animation_index == 2:
            self.first_entry = False
            self.focus_index = -1
            self.word_list = []
            self.anim_group.add(self.animation_6)
            self.word_group.empty()
            self.text_bg_group.empty()
            self.anim_group.add(self.animation_6_3)
            self.animation_6.detener()
            self.speech_server.processtext(
                self.screen_text("anim_1"),
                self.parent.config.is_screen_reader_enabled(),
            )

        elif animation_index == 3:
            self.focus_index = -1
            self.word_group.empty()
            self.anim_group.remove(self.animation_6_3)
            self.text_bg_group.add(self.caja_texto)
            self.word_group.add(self.texto6_3.words)
            self.txt_actual = self.texto6_3.words
            self.collect_words(self.txt_actual)
            self.speech_server.processtext(
                self.screen_text("text_3"),
                self.parent.config.is_screen_reader_enabled(),
            )
            self.animation_6.continuar()

        elif animation_index == 4:
            self.focus_index = -1
            self.anim_group.remove(self.animation_6_4)
            self.word_group.empty()
            self.anim_group.remove(self.animation_6_3)
            self.text_bg_group.add(self.caja_texto)
            self.word_group.add(self.texto6_4.words)
            self.txt_actual = self.texto6_4.words
            self.collect_words(self.txt_actual)
            self.speech_server.processtext(
                self.screen_text("text_4"),
                self.parent.config.is_screen_reader_enabled(),
            )
            self.animation_6.continuar()

        elif animation_index == 5:
            self.focus_index = -1
            self.word_list = []
            self.word_group.empty()
            self.text_bg_group.empty()
            self.animation_6_4.update()
            self.animation_6_4.stop = False
            self.anim_group.add(self.animation_6_4)
            self.animation_6.detener()
            self.speech_server.processtext(
                self.screen_text("anim_2"),
                self.parent.config.is_screen_reader_enabled(),
            )

        elif animation_index == 6:
            self.focus_index = -1
            self.anim_group.remove(self.animation_6_4)
            self.word_group.remove(self.texto7_3.words)
            self.text_bg_group.add(self.caja_texto)
            self.word_group.add(self.texto7_2.words)
            self.txt_actual = self.texto7_2.words
            self.collect_words(self.txt_actual)
            self.speech_server.processtext(
                self.screen_text("text_5"),
                self.parent.config.is_screen_reader_enabled(),
            )
            self.animation_6.continuar()

        elif animation_index == 7:
            self.focus_index = -1
            self.word_group.empty()
            self.text_bg_group.add(self.caja_texto)
            self.word_group.add(self.texto7_3.words)
            self.txt_actual = self.texto7_3.words
            self.collect_words(self.txt_actual)
            self.speech_server.processtext(
                self.screen_text("text_6"),
                self.parent.config.is_screen_reader_enabled(),
            )
            self.animation_6.continuar()

        elif animation_index == 8:
            self.focus_index = -1
            self.word_group.empty()
            self.text_bg_group.add(self.caja_texto)
            self.word_group.add(self.texto7_4.words)
            self.txt_actual = self.texto7_4.words
            self.collect_words(self.txt_actual)
            self.speech_server.processtext(
                self.screen_text("text_7"),
                self.parent.config.is_screen_reader_enabled(),
            )
            self.animation_6.continuar()

        elif animation_index == 9:
            self.focus_index = -1
            self.anim_group.remove(self.animation_6_5)
            self.word_group.empty()
            self.text_bg_group.add(self.caja_texto)
            self.word_group.add(self.texto7_5.words)
            self.txt_actual = self.texto7_5.words
            self.collect_words(self.txt_actual)
            self.speech_server.processtext(
                self.screen_text("text_8"),
                self.parent.config.is_screen_reader_enabled(),
            )
            self.animation_6.continuar()

        elif animation_index == 10:
            self.focus_index = -1
            self.word_list
            self.word_group.empty()
            self.text_bg_group.empty()
            self.animation_6_5.update()
            self.animation_6_5.stop = False
            self.anim_group.add(self.animation_6_5)
            self.animation_6.detener()
            self.speech_server.processtext(
                self.screen_text("anim_3"),
                self.parent.config.is_screen_reader_enabled(),
            )

        elif animation_index == 11:
            self.focus_index = -1
            self.anim_group.remove(self.animation_6_6)
            self.anim_group.remove(self.animation_6_5)
            self.text_bg_group.add(self.caja_texto)
            self.word_group.add(self.texto7_6.words)
            self.button_group.add(self.next)
            self.txt_actual = self.texto7_6.words
            self.collect_words(self.txt_actual)
            self.speech_server.processtext(
                self.screen_text("text_9"),
                self.parent.config.is_screen_reader_enabled(),
            )
            self.animation_6.continuar()

        elif animation_index == 12:
            self.focus_index = -1
            self.tooltip_group.empty()
            self.word_group.empty()
            self.text_bg_group.empty()
            self.animation_6_6.update()
            self.animation_6_6.stop = False
            self.button_group.remove(self.next)
            self.anim_group.add(self.animation_6_6)
            self.animation_6.detener()
            self.speech_server.processtext(
                self.screen_text("anim_4"),
                self.parent.config.is_screen_reader_enabled(),
            )

    def update(self):
        """Update cursor position, magnifier, button tooltips, and trigger the first text display after the initial delay."""
        self.mouse.update()
        self.magnifier.magnificar(self.parent.screen)
        self.button_group.update(self.tooltip_group)

        if self.current_anim == 1 and not self.parent.config.is_screen_reader_enabled():
            if not self.elapsed_ms < 1000:
                self.anim_group.add(self.animation_6_2)
                self.text_bg_group.add(self.caja_texto)
                self.word_group.add(self.texto6_2.words)
                self.txt_actual = self.texto6_2.words
                self.collect_words(self.txt_actual)
                self.animation_6.continuar()
        self.elapsed_ms += self.frame_clock.get_time()

    def go_to_glossary(self):
        self.parent.pushState(pantalla10.Screen(self.parent))
