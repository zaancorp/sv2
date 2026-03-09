#!/usr/bin/env python
"""Content screen covering plant reproduction (continued) and photosynthesis (screens 6–7)."""

import pygame

from components import screen
from components.image import Image

from paginas import pantalla5

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

        # Text steps use animation_6 as the main illustration.
        # Anim steps (2, 5, 10, 12) play a sub-animation on top of the stopped animation_6.
        # animation_6_2 stays in anim_group as a secondary background at all steps.
        self.animation_states = {
            1:  (self.animation_6,   self.texto6_2, "text_2"),
            2:  (self.animation_6_3, None,          "anim_1"),
            3:  (self.animation_6,   self.texto6_3, "text_3"),
            4:  (self.animation_6,   self.texto6_4, "text_4"),
            5:  (self.animation_6_4, None,          "anim_2"),
            6:  (self.animation_6,   self.texto7_2, "text_5"),
            7:  (self.animation_6,   self.texto7_3, "text_6"),
            8:  (self.animation_6,   self.texto7_4, "text_7"),
            9:  (self.animation_6,   self.texto7_5, "text_8"),
            10: (self.animation_6_5, None,          "anim_3"),
            11: (self.animation_6,   self.texto7_6, "text_9"),
            12: (self.animation_6_6, None,          "anim_4"),
        }

        self.button_actions = {
            "home":   self.go_home,
            "config": self.go_config,
            "back":   self.go_back,
            "next":   self.go_next,
        }

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

    def go_back(self):
        self.current_anim -= 1
        self.reproducir_animacion(self.current_anim)

    def go_next(self):
        if self.current_anim <= 13:
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
            return

        if animation_index in self.animation_states:
            animation_obj, text_obj, text_key = self.animation_states[animation_index]
            self.setup_animation(animation_obj, text_obj, text_key)

            # animation_6_2 stays in anim_group as a secondary background at every step.
            self.anim_group.add(self.animation_6_2)

            # Anim steps (2, 5, 10, 12): keep animation_6 as a stopped background.
            # Steps 5, 10, 12 also need the sub-animation's playback state reset;
            # step 2 plays animation_6_3 from its current position without reset.
            if animation_index in (2, 5, 10, 12):
                self.anim_group.add(self.animation_6)
                self.animation_6.detener()
                if animation_index != 2:
                    animation_obj.update()
                    animation_obj.stop = False

            # Per-step specials
            if animation_index == 1:
                if self.parent.config.is_screen_reader_enabled() and self.first_entry:
                    self.speech_server.processtext2(
                        self.screen_text("text_2"),
                        self.parent.config.is_screen_reader_enabled(),
                    )
                    self.first_entry = False
            elif animation_index == 2:
                self.first_entry = False
            elif animation_index == 11:
                self.button_group.add(self.next)
            elif animation_index == 12:
                self.tooltip_group.empty()
                self.button_group.remove(self.next)

        self.collect_buttons(self.button_group)
        self.nav_list = self.word_list + self.button_list
        self.element_count = len(self.nav_list)

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


