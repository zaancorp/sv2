#!/usr/bin/env python3
"""Developer scratch screen used for manual testing; not part of the production flow."""

import pygame

from sv2.src.components import screen
from paginas import pantalla2

banners = ["banner-inf"]

buttons = ["intro"]


class Screen(screen.Screen):
    """Playground screen used during development to test UI components in isolation."""

    def __init__(self, parent, is_overlay=False):
        """
        Initialise the playground screen.

        @param parent: Screen manager instance.
        @type parent: Manejador
        @param is_overlay: True if pushed over another screen; False if loaded via changeState.
        @type is_overlay: bool
        """

        self.name = "screen_2"
        super().__init__(parent, self.name)

        self.load_banners(banners)
        self.load_buttons(buttons)
        self.load_instruction_images()

    def load_instruction_images(self):
        """Load image assets used in the instruction overlay."""
        self.img1 = pygame.image.load(self.popups_path + "touch.png").convert_alpha()
        self.img2 = pygame.image.load(self.popups_path + "flechas.png").convert_alpha()
        self.img3 = pygame.image.load(self.popups_path + "enter.png").convert_alpha()
        self.img4 = pygame.image.load(self.popups_path + "f1.png").convert_alpha()
        self.img5 = pygame.image.load(self.popups_path + "sordo.png").convert_alpha()
        self.img6 = pygame.image.load(self.popups_path + "visual.png").convert_alpha()
        self.dic_img = {
            "RATON": self.img1,
            "TECLAS": self.img2,
            "ENTER": self.img3,
            "F1": self.img4,
            "DFA": self.img5,
            "DFV": self.img6,
        }

    def start(self):
        self.resume()

    def cleanUp(self):
        pass

    def pause(self):
        pass

    def resume(self):
        """Reload buttons and populate sprite groups."""

        self.load_buttons(buttons)
        self.banner_group.add(self.banner_inf)
        self.button_group.add(self.intro)

    def handleEvents(self, events):
        """
        Process input events for this screen.

        @param events: Event list from the main loop.
        @type events: list
        """

        self.teclasPulsadas = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.QUIT:
                self.parent.quit()

            if event.type == pygame.KEYDOWN:
                self.collect_buttons(self.button_group)
                self.element_count = len(self.button_list)

                if event.key == pygame.K_RIGHT:
                    if self.focus_index < self.element_count:
                        self.focus_index += 1
                        if self.focus_index >= self.element_count:
                            self.focus_index = self.element_count - 1
                        self.x = self.button_list[self.focus_index]
                        self.speech_server.processtext(self.x.tooltip, True)
                        self.set_focus_rect(self.x.rect)
                        self.keyboard_nav_active = True

                elif event.key == pygame.K_LEFT:
                    if self.focus_index > 0:
                        self.focus_index -= 1
                        if self.focus_index <= 0:
                            self.focus_index = 0
                        self.x = self.button_list[self.focus_index]
                        self.speech_server.processtext(self.x.tt, True)
                        self.set_focus_rect(self.x.rect)
                        self.keyboard_nav_active = True

                elif self.keyboard_nav_active:
                    if event.key == pygame.K_RETURN:
                        self.focus_index = -1
                        if self.x.obj_type == "button":
                            if self.x.id == "intro":
                                self.clear_groups()
                                self.parent.changeState(pantalla2.Screen(self.parent))

                            elif self.x.id == "puerta":
                                self.clear_groups()
                                self.parent.popState()

            if pygame.sprite.spritecollideany(self.mouse, self.button_group):
                sprite = pygame.sprite.spritecollide(
                    self.mouse, self.button_group, False
                )
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.speech_server.stopserver()
                    if sprite[0].id == "intro":
                        self.clear_groups()
                        self.parent.changeState(pantalla2.Screen(self.parent))

                    elif sprite[0].id == "puerta":
                        self.clear_groups()
                        self.parent.popState()

        self.handle_magnifier(events)

    def update(self):
        """Update cursor position, magnifier, and button tooltips."""

        self.mouse.update()
        self.magnifier.magnificar(self.parent.screen)
        self.button_group.update(self.tooltip_group)

    def draw(self):
        """Draw the background and all sprite groups onto the screen manager surface."""

        self.parent.screen.blit(self.background, (0, 0))
        self.banner_group.draw(self.parent.screen)
        self.button_group.draw(self.parent.screen)
        self.text_bg_group.draw(self.parent.screen)
        self.word_group.draw(self.parent.screen)
        self.tooltip_group.draw(self.parent.screen)
        self.popup_group.draw(self.parent.screen)
        if self.parent.magnifier_active:
            self.magnifier_group.draw(self.parent.screen, self.enable)
        self.draw_focus_rect()
        self.draw_debug_rectangles()
