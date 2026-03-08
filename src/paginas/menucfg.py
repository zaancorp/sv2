#!/usr/bin/env python

import pygame

from components import screen
from components.popups import PopUp
from components.image import Image
from paginas import pantalla2, menuauditivo, menuvisual, menugeneral

buttons = [
    "puerta",
    "deaf-menu-btn",
    "visual-menu-btn",
    "general-menu-btn",
    "intro",
]


class Screen(screen.Screen):
    """Accessibility configuration menu screen — the first screen shown to the user."""

    def __init__(self, parent, is_overlay=False):
        """
        Initialise the screen.

        @param parent: Screen manager instance.
        @type parent: Manejador
        @param is_overlay: True if this screen is pushed over another; False if loaded via changeState.
        @type is_overlay: bool
        """

        self.name = "screen_1"

        super().__init__(parent, self.name)

        self.is_overlay = is_overlay

        self.fondo_simple = pygame.image.load(
            self.backgrounds_path + "background-simple.png"
        ).convert()

        self.banner_inf = Image(
            0,
            432,
            self.banners_path + "banner-inf.png",
        )

        self.banner_config = Image(
            0,
            0,
            self.banners_path + "banner-acc.png",
        )

        self.load_buttons(buttons)

        self.load_instruction_images()
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.button_actions = {
            "intro":            lambda: (self.clear_groups(), self.parent.changeState(pantalla2.Screen(self.parent))),
            "puerta":           lambda: (self.clear_groups(), self.parent.popState()),
            "deaf-menu-btn":    lambda: (self.clear_groups(), self.parent.pushState(menuauditivo.Screen(self.parent, self.is_overlay))),
            "visual-menu-btn":  lambda: (self.clear_groups(), self.parent.pushState(menuvisual.Screen(self.parent, self.is_overlay))),
            "general-menu-btn": lambda: (self.clear_groups(), self.parent.pushState(menugeneral.Screen(self.parent, self.is_overlay))),
        }

    def load_instruction_images(self):
        """Load the images used in the initial instructions popup."""
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

    def resume(self):
        """Restore the screen state, loading the appropriate buttons depending on whether this is the first visit."""
        if self.parent.RETURN_TO_PREV_SCREEN:
            self.parent.RETURN_TO_PREV_SCREEN = False
            self.clear_groups()
            self.parent.popState()
        else:
            if self.parent.first_run:
                self.load_buttons(buttons)
                self.banner_group.add(self.banner_inf)
                self.button_group.add(self.deaf_menu_btn, self.visual_menu_btn, self.general_menu_btn, self.intro)
                if self.parent.config.is_show_popups_enabled():
                    self.popup_ins = PopUp(
                        self.parent,
                        self.parent.text_loader.popup(self.name, "text_1"),
                        "",
                        self.dic_img,
                        self.popup_group,
                        2,
                        512,
                        290,
                        100,
                    )
                    self.popup_ins.add_to_group()
                    self.speech_server.processtext(
                        self.parent.text_loader.popup(self.name, "reader_1"), True
                    )
            else:
                self.background = self.fondo_simple
                if self.parent.config.is_text_change_enabled():
                    self.load_buttons(buttons)
                    self.parent.config.set_text_change_enabled(False)
                if self.parent.config.is_show_popups_enabled():
                    self.popup_ins = PopUp(
                        self.parent,
                        self.parent.text_loader.popup(self.name, "text_2"),
                        "",
                        self.dic_img,
                        self.popup_group,
                        2,
                        512,
                        270,
                        100,
                    )
                    self.popup_ins.add_to_group()
                    self.speech_server.processtext(
                        self.parent.text_loader.popup(self.name, "reader_2"), True
                    )
                self.banner_group.add(self.banner_config, self.banner_inf)
                self.button_group.add(self.deaf_menu_btn, self.visual_menu_btn, self.general_menu_btn, self.puerta)

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
                    self.nav_left()
                elif self.keyboard_nav_active and event.key == pygame.K_RETURN:
                    self.keyboard_nav_active = False
                    if self.x.obj_type == "button":
                        self.button_actions.get(self.x.id, lambda: None)()

            elif pygame.sprite.spritecollideany(self.mouse, self.button_group):
                sprite = pygame.sprite.spritecollide(self.mouse, self.button_group, False)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.speech_server.stopserver()
                    self.button_actions.get(sprite[0].id, lambda: None)()

        self._rebuild_nav()
        self.handle_magnifier(events)

