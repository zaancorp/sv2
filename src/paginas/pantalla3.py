#!/usr/bin/env python
"""Content screen introducing the Plants unit (screen 3)."""

import pygame

from components import screen
from components.image import Image

from paginas import menucfg
from paginas import pantalla2
from paginas import pantalla4
from paginas import pantalla10

animations = [
    "animation-3",
]

banners = [
    "banner-inf",
    "banner-plantas",
]

buttons = [
    "home",
    "config",
    "next",
]


class Screen(screen.Screen):
    """Screen presenting introductory content about plants with animation and rich text."""

    def __init__(self, parent):
        """
        Initialise the screen.

        @param parent: Screen manager instance.
        @type parent: Manejador
        """

        self.name = "screen_3"
        super().__init__(parent, self.name)

        # Add to the banners

        self.caja_texto = Image(0, 332, self.backgrounds_path + "caja-texto.png")

        self.load_animations(animations)
        self.load_banners(banners)
        self.load_buttons(buttons)
        self.load_texts()

    def load_texts(self):
        """Load and build the text objects used on this screen."""
        texts = self.load_screen_texts(["text_2"], x=32, right_limit=992)
        self.texto3_2 = texts["text_2"]

    def start(self):
        self.resume()

    def resume(self):
        """Reload buttons and texts if config changed, then initialise sprite groups and animation state."""
        if self.parent.config.is_text_change_enabled():
            self.load_texts()
            self.load_buttons(buttons)
            self.parent.config.set_text_change_enabled(False)
        self.anim_group.add(self.animation_3)
        self.banner_group.add(self.banner_plantas, self.banner_inf)
        self.button_group.add(self.config, self.next, self.home)
        self.elapsed_ms = 0
        self.creado = True
        self.animation_3.detener()
        self.speech_server.stopserver()
        self.first_entry = True
        self.speech_server.processtext(
            "Pantalla: Las Plantas", self.parent.config.is_screen_reader_enabled()
        )
        if self.parent.config.is_screen_reader_enabled():
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
                            if self.x.id == "config":
                                self.clear_groups()
                                self.parent.pushState(
                                    menucfg.Screen(self.parent, self.is_overlay)
                                )

                            elif self.x.id == "next":
                                self.ampliar()
                                self.clear_groups()
                                self.parent.changeState(pantalla4.Screen(self.parent))

                            elif self.x.id == "home":
                                self.clear_groups()
                                self.parent.changeState(pantalla2.Screen(self.parent))

                        elif self.x.obj_type == "word":
                            self.speech_server.processtext(
                                self.parent.text_loader.concept(self.x.codigo),
                                self.parent.config.is_screen_reader_enabled(),
                            )
                        self.keyboard_nav_active = False

                elif event.key == pygame.K_SPACE:
                    self.speech_server.processtext(
                        self.screen_text("text_2"),
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
                    if sprite[0].id == "next":
                        self.keyboard_nav_active = False
                        if self.current_anim <= 3:
                            self.current_anim += 1
                            self.reproducir_animacion(self.current_anim)

                    elif sprite[0].id == "config":
                        self.clear_groups()
                        self.parent.pushState(menucfg.Screen(self.parent, self.is_overlay))

                    elif sprite[0].id == "home":
                        self.clear_groups()
                        self.parent.changeState(pantalla2.Screen(self.parent))
                    elif sprite[0].id == "repe":
                        self.clear_groups()
                        self.resume()
        self.handle_magnifier(events)

    def reproducir_animacion(self, animation_index):
        """
        Advance the screen to the given animation step, updating sprite groups and TTS accordingly.

        @param animation_index: Index of the animation step to display.
        @type animation_index: int
        """
        if animation_index == 0:
            self.focus_index = -1
            self.animation_3.continuar()
            self.text_bg_group.add(self.caja_texto)
            self.word_group.add(self.texto3_2.words)
            self.txt_actual = self.texto3_2.words
            self.collect_words(self.txt_actual)

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
                self.animation_3.continuar()
                self.text_bg_group.add(self.caja_texto)
                self.word_group.add(self.texto3_2.words)
                self.txt_actual = self.texto3_2.words
                self.collect_words(self.txt_actual)

        if animation_index == 1:
            self.speech_server.stopserver()
            self.focus_index = -1
            self.ampliar()
            self.clear_groups()
            self.parent.changeState(pantalla4.Screen(self.parent))

        self.collect_buttons(self.button_group)
        self.nav_list = self.button_list + self.word_list
        self.nav_list = self.word_list + self.button_list
        self.element_count = len(self.nav_list)

    def update(self):
        """Update cursor position, magnifier, button tooltips, and trigger animation start after the initial delay."""
        self.mouse.update()
        self.magnifier.magnificar(self.parent.screen)
        self.button_group.update(self.tooltip_group)
        if not self.parent.config.is_screen_reader_enabled():
            if not self.elapsed_ms < 1000:
                self.animation_3.continuar()
                self.text_bg_group.add(self.caja_texto)
                self.word_group.add(self.texto3_2.words)
                self.txt_actual = self.texto3_2.words
                self.collect_words(self.txt_actual)
        self.elapsed_ms += self.frame_clock.get_time()

    def draw(self):
        """Draw the background and all sprite groups onto the screen manager surface."""
        self.parent.screen.blit(self.background, (0, 0))
        self.anim_group.draw(self.parent.screen)
        self.banner_group.draw(self.parent.screen)
        self.button_group.draw(self.parent.screen)
        self.text_bg_group.draw(self.parent.screen)
        self.word_group.draw(self.parent.screen)
        self.tooltip_group.draw(self.parent.screen)
        self.popup_group.draw(self.parent.screen)
        if self.parent.magnifier_active:
            self.magnifier_group.draw(self.parent.screen, self.enable)
        if self.keyboard_nav_active:
            self.draw_focus_rect()
        self.draw_debug_rectangles()

    def ampliar(self):
        """Play a smooth zoom-in transition towards the bottom-right corner of the background."""
        rx = self.background.get_width()
        ry = self.background.get_height()
        div = self.mcd(rx, ry)
        px = 0
        py = 0
        vx = 1
        vy = 1
        esc = 1.0 / div
        for _ in range(1, div + 1):
            px -= rx / div
            py -= ry / div
            vx += esc
            vy += esc
            fondo_amp = pygame.transform.smoothscale(
                self.background, (int(rx * vx), int(ry * vy))
            )
            self.parent.screen.blit(fondo_amp, (px, py))
            pygame.time.delay(30)
            pygame.display.update()

    def mcd(self, x, y):
        if y == 0:
            return x
        else:
            return self.mcd(y, x % y)

    def go_to_glossary(self):
        self.parent.pushState(pantalla10.Screen(self.parent))
