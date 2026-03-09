#!/usr/bin/env python
"""Content screen covering plant reproduction (screen 5)."""

import pygame

from components import screen
from components.image import Image

from paginas import pantalla6

animations = [
    "animation-5",
    "animation-5-0",
    "animation-5-1",
    "animation-5-2",
    "animation-5-3",
]

banners = [
    "banner-inf",
    "banner-repro",
]

buttons = [
    "home",
    "next",
    "config",
    "back",
]


class Screen(screen.Screen):
    """Screen presenting plant reproduction content through sequenced animations and rich text."""

    def __init__(self, parent, current_anim=0):
        """
        Initialise the screen.

        @param parent: Screen manager instance.
        @type parent: Manejador
        @param current_anim: Index of the animation step to resume from; 0 means start from the beginning.
        @type current_anim: int
        """

        self.name = "screen_5"
        super().__init__(parent, self.name)

        # Animations

        self.current_anim = current_anim

        self.load_animations(animations)
        self.load_banners(banners)
        self.load_buttons(buttons)
        self.load_texts()

        # Banners
        self.caja_texto = Image(0, 332, self.backgrounds_path + "caja-texto.png")

        self.update_group.add(
            self.animation_5, self.animation_5_0, self.animation_5_1, self.animation_5_2
        )

        self.animation_states = {
            1: (self.animation_5, self.texto5_2, "text_2"),
            2: (self.animation_5_3, None, "anim_1"),
            3: (self.animation_5, self.texto5_3, "text_3"),
            4: (self.animation_5_0, None, "anim_2"),
            5: (self.animation_5, self.texto5_4, "text_4"),
            6: (self.animation_5_1, None, "anim_3"),
            7: (self.animation_5, self.texto5_5, "text_5"),
            8: (self.animation_5_2, None, "anim_4"),
            9: (self.animation_5, self.texto5_6, "text_6"),
        }

        self.button_actions = {
            "home":   self.go_home,
            "config": self.go_config,
            "back":   self.go_back,
            "next":   self.go_next,
        }

    def load_texts(self):
        texts = self.load_screen_texts(
            ["text_2", "text_3", "text_4", "text_5", "text_6"], x=64, right_limit=960
        )
        self.texto5_2 = texts["text_2"]
        self.texto5_3 = texts["text_3"]
        self.texto5_4 = texts["text_4"]
        self.texto5_5 = texts["text_5"]
        self.texto5_6 = texts["text_6"]

    def start(self):
        self.resume()

    def resume(self):
        """Reload buttons and texts if config changed, then initialise sprite groups and start the current animation step."""
        if self.parent.config.is_text_change_enabled():
            self.load_buttons(buttons)
            self.load_texts()
            self.parent.config.set_text_change_enabled(False)
        self.anim_group.add(self.animation_5)
        self.image_group.add(self.animation_5_3)
        self.banner_group.add(self.banner_repro, self.banner_inf)
        self.button_group.add(self.config, self.next, self.back, self.home)
        self.animation_5.detener()
        self.animation_5_3.detener()
        self.creado = True
        self.elapsed_ms = 0
        if self.current_anim == 0:
            self.current_anim = 1
        self.speech_server.processtext(
            "Pantalla: Reproducción de las plantas.", self.parent.config.is_screen_reader_enabled()
        )
        self.reproducir_animacion(self.current_anim)
        self.first_entry = True

    def go_back(self):
        self.current_anim -= 1
        self.reproducir_animacion(self.current_anim)

    def go_next(self):
        self.current_anim += 1
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

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.keyboard_nav_active = True
                    self.nav_right()
                elif event.key == pygame.K_LEFT:
                    self.keyboard_nav_active = True
                    self.nav_left()
                elif self.keyboard_nav_active and event.key == pygame.K_RETURN:
                    self.keyboard_nav_active = False
                    if self.x.obj_type == "button":
                        self.button_actions.get(self.x.id, lambda: None)()
                    elif self.x.obj_type == "word":
                        self.speech_server.processtext(
                            self.parent.text_loader.concept(self.x.code),
                            self.parent.config.is_screen_reader_enabled(),
                        )

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.sprite.spritecollideany(self.mouse, self.word_group):
                    sprite = pygame.sprite.spritecollide(self.mouse, self.word_group, False)
                    if sprite[0].interpretable:
                        self.parent.show_concept(sprite[0].code)
                elif pygame.sprite.spritecollideany(self.mouse, self.button_group):
                    sprite = pygame.sprite.spritecollide(self.mouse, self.button_group, False)
                    self.speech_server.stopserver()
                    self.button_actions.get(sprite[0].id, lambda: None)()

        self._rebuild_nav()
        self.handle_magnifier(events)

    def update(self):
        """Update cursor position, magnifier, button tooltips, and trigger the first text display after the initial delay."""
        self.mouse.update()
        self.magnifier.magnificar(self.parent.screen)
        self.button_group.update(self.tooltip_group)
        if self.current_anim == 1 and not self.parent.config.is_screen_reader_enabled():
            if not self.elapsed_ms < 1000:
                self.text_bg_group.add(self.caja_texto)
                self.word_group.add(self.texto5_2.words)
                self.txt_actual = self.texto5_2.words
                self.collect_words(self.txt_actual)
                self.animation_5.continuar()
        self.elapsed_ms += self.frame_clock.get_time()

    def reproducir_animacion(self, animation_index):
        if 1 <= animation_index <= 9:
            animation_obj, text_obj, text_key = self.animation_states[animation_index]
            self.setup_animation(animation_obj, text_obj, text_key)

            if animation_index == 1:
                self.button_group.remove(self.back)
                if self.parent.config.is_screen_reader_enabled() and self.first_entry:
                    self.speech_server.processtext2(
                        self.screen_text("text_2"),
                        self.parent.config.is_screen_reader_enabled(),
                    )
                    self.first_entry = False
            elif animation_index == 2:
                self.first_entry = False
                self.button_group.empty()
                self.button_group.add(self.config, self.back, self.next, self.home)
                self.animation_5.detener()
                self.animation_5_3.update()
                self.animation_5_3.stop = False
            elif animation_index == 9:
                self.button_group.add(self.back)

        elif animation_index == 10:
            self.clear_groups()
            self.parent.changeState(pantalla6.Screen(self.parent))

        self.collect_buttons(self.button_group)
        self.nav_list = self.word_list + self.button_list
        self.element_count = len(self.nav_list)


