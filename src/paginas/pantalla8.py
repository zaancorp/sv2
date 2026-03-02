#!/usr/bin/env python
"""Content screen covering agriculture in Venezuela (screen 8)."""

import pygame

from components import screen
from components.image import Image

from paginas import menucfg
from paginas import pantalla2
from paginas import pantalla9
from paginas import pantalla10

animations = [
    "animation-8",
    "animation-8-0",
]

banners = [
    "banner-inf",
    "banner-agri",
]

buttons = [
    "home",
    "next",
    "back",
    "config",
]


class Screen(screen.Screen):
    """Screen presenting content about agriculture in Venezuela with a tractor background animation."""

    def __init__(self, parent, current_anim=0):
        """
        Initialise the screen.

        @param parent: Screen manager instance.
        @type parent: Manejador
        @param current_anim: Index of the animation step to resume from; 0 means start from the beginning.
        @type current_anim: int
        """

        self.name = "screen_8"
        super().__init__(parent, self.name)

        self.current_anim = current_anim

        pygame.display.set_caption("Sembrando para el futuro")

        # Banners

        self.caja_texto = Image(0, 332, self.backgrounds_path + "caja-texto.png")

        self.load_animations(animations)
        self.load_banners(banners)
        self.load_buttons(buttons)
        self.load_texts()

        # These two are used by the tractor animation in the background
        self.elapsed_ms = 0
        self.tractor = -2

    def load_texts(self):
        """Load and build the text objects used on this screen."""
        texts = self.load_screen_texts(["text_2", "text_3", "text_4"], x=32, right_limit=992)
        self.texto8_2 = texts["text_2"]
        self.texto8_3 = texts["text_3"]
        self.texto8_4 = texts["text_4"]

    def start(self):
        self.resume()

    def resume(self):
        """Reload buttons and texts if config changed, then initialise sprite groups and start the current animation step."""
        if self.parent.config.is_text_change_enabled():
            self.load_buttons(buttons)
            self.load_texts()
            self.parent.config.set_text_change_enabled(False)
        self.anim_group.add(self.animation_8)
        self.image_group.add(self.animation_8_0)
        self.banner_group.add(self.banner_agri, self.banner_inf)
        self.button_group.add(self.config, self.next, self.home)
        self.creado = True
        if self.current_anim == 0:
            self.current_anim = 1
        self.first_entry = True
        self.speech_server.processtext(
            "Pantalla: La Agricultura en Venezuela: ", self.parent.config.is_screen_reader_enabled()
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
                if event.key == pygame.K_RIGHT:
                    self.nav_right()
                    self.keyboard_nav_active = True

                elif event.key == pygame.K_LEFT:
                    self.nav_left()

                elif self.keyboard_nav_active:
                    if event.key == pygame.K_RETURN:
                        if self.x.obj_type == "button":
                            if self.x.id == "config":
                                self.clear_groups()
                                self.parent.pushState(
                                    menucfg.Screen(self.parent, self.is_overlay)
                                )
                                self.keyboard_nav_active = False

                            elif self.x.id == "next":
                                if self.current_anim <= 11:
                                    self.current_anim += 1
                                    self.reproducir_animacion(self.current_anim)
                                self.keyboard_nav_active = False

                            elif self.x.id == "back":
                                if self.current_anim > 0:
                                    self.current_anim -= 1
                                    self.reproducir_animacion(self.current_anim)
                                    if self.current_anim <= 0:
                                        self.current_anim = 0
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
                    elif sprite[0].id == "next":
                        self.repeticion = True
                        self.keyboard_nav_active = False
                        if self.current_anim <= 11:
                            self.current_anim += 1
                            self.reproducir_animacion(self.current_anim)
                    elif sprite[0].id == "back":
                        self.keyboard_nav_active = False
                        if self.current_anim > 0:
                            self.current_anim -= 1
                            self.reproducir_animacion(self.current_anim)
                    elif sprite[0].id == "repe":
                        self.clear_groups()
                        self.resume()
        self.handle_magnifier(events)

    def update(self):
        """Update cursor position, magnifier, button tooltips, advance the tractor animation, and trigger the first text display after the initial delay."""
        self.mouse.update()
        self.magnifier.magnificar(self.parent.screen)
        self.button_group.update(self.tooltip_group)
        self.animation_8_0.rect.move_ip(self.tractor, 0)
        # Movimiento del tractor
        if self.animation_8_0.rect.left + self.animation_8_0.rect.width + 100 < 0:
            self.tractor = self.tractor * -1
            self.animation_8_0.image = pygame.transform.flip(
                self.animation_8_0.image, True, False
            )
            self.animation_8_0.image = pygame.transform.smoothscale(
                self.animation_8_0.image,
                (self.animation_8_0.rect.width / 2, self.animation_8_0.rect.height / 2),
            )

        if self.animation_8_0.rect.left > 1124:
            self.tractor = self.tractor * -1
            self.animation_8_0.image = pygame.transform.flip(
                self.animation_8_0.image, True, False
            )
            self.animation_8_0.image = self.animation_8_0.img
        # Automatizado del inicio de pantalla
        if self.current_anim == 1 and not self.parent.config.is_screen_reader_enabled():
            if not self.elapsed_ms < 1000:
                self.text_bg_group.add(self.caja_texto)
                self.word_group.add(self.texto8_2.words)
                self.txt_actual = self.texto8_2.words
        self.elapsed_ms += self.frame_clock.get_time()

    def reproducir_animacion(self, animation_index):
        """
        Advance the screen to the given animation step, updating sprite groups and TTS accordingly.

        @param animation_index: Index of the animation step to display.
        @type animation_index: int
        """
        if animation_index == 1:
            self.focus_index = -1
            self.text_bg_group.empty()
            self.tooltip_group.empty()
            self.button_group.remove(self.back)
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
                self.word_group.add(self.texto8_2.words)
                self.txt_actual = self.texto8_2.words
                self.collect_words(self.txt_actual)

        elif animation_index == 2:
            self.first_entry = False
            self.focus_index = -1
            self.word_group.empty()
            self.button_group.empty()
            self.button_group.add(self.config, self.back, self.next, self.home)
            self.text_bg_group.add(self.caja_texto)
            self.word_group.add(self.texto8_3.words)
            self.txt_actual = self.texto8_3.words
            self.collect_words(self.txt_actual)
            self.speech_server.processtext(
                self.screen_text("text_3"),
                self.parent.config.is_screen_reader_enabled(),
            )

        elif animation_index == 3:
            self.focus_index = -1
            self.word_group.empty()
            self.button_group.empty()
            self.button_group.add(self.config, self.back, self.next, self.home)
            self.text_bg_group.add(self.caja_texto)
            self.word_group.add(self.texto8_4.words)
            self.txt_actual = self.texto8_4.words
            self.collect_words(self.txt_actual)
            self.speech_server.processtext(
                self.screen_text("text_4"),
                self.parent.config.is_screen_reader_enabled(),
            )

        elif animation_index == 4:
            self.clear_groups()
            self.parent.changeState(pantalla9.Screen(self.parent))

        self.collect_buttons(self.button_group)
        self.nav_list = self.word_list + self.button_list
        self.element_count = len(self.nav_list)

    def go_to_glossary(self):
        self.parent.pushState(pantalla10.Screen(self.parent))
