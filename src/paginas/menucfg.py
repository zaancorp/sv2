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

        self.parent = parent

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
                # self.popup_ins = PopUp(
                #     self.parent,
                #     # TODO: If the parent is already being passed we can grab the
                #     # text from the parent's dict, we would only need to pass the
                #     # screen name and maybe the "popups" key
                #     self.parent.text_content["popups"][self.name]["text_1"],
                #     "",
                #     self.dic_img,
                #     self.popup_group,
                #     2,
                #     512,
                #     290,
                #     100,
                # )

                # self.popup_ins.add_to_group()
                # self.speech_server.processtext(
                #     self.parent.text_content["popups"][self.name]["reader_1"], True
                # )
            else:
                self.background = self.fondo_simple
                if self.parent.config.is_text_change_enabled():
                    self.load_buttons(buttons)
                    self.parent.config.set_text_change_enabled(False)
                # self.popup_ins = PopUp(
                #     self.parent,
                #     self.parent.text_content["popups"][self.name]["text_2"],
                #     "",
                #     self.dic_img,
                #     self.popup_group,
                #     2,
                #     512,
                #     270,
                #     100,
                # )
                # self.popup_ins.add_to_group()
                # self.speech_server.processtext(
                #     self.parent.text_content["popups"][self.name]["reader_2"], True
                # )
                self.banner_group.add(self.banner_config, self.banner_inf)
                self.button_group.add(self.deaf_menu_btn, self.visual_menu_btn, self.general_menu_btn, self.puerta)

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
                        self.speech_server.processtext(self.x.tt, True)
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
                            if self.x.id == "sordo":
                                self.clear_groups()
                                self.parent.pushState(
                                    menuauditivo.Screen(self.parent, self.is_overlay)
                                )

                            elif self.x.id == "config-vis":
                                self.clear_groups()
                                self.parent.pushState(
                                    menuvisual.Screen(self.parent, self.is_overlay)
                                )

                            elif self.x.id == "general-menu-btn":
                                self.clear_groups()
                                self.parent.pushState(
                                    menugeneral.Screen(self.parent, self.is_overlay)
                                )

                            elif self.x.id == "intro":
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

                    elif sprite[0].id == "deaf-menu-btn":
                        self.clear_groups()
                        self.parent.pushState(
                            menuauditivo.Screen(self.parent, self.is_overlay)
                        )

                    elif sprite[0].id == "visual-menu-btn":
                        self.clear_groups()
                        self.parent.pushState(
                            menuvisual.Screen(self.parent, self.is_overlay)
                        )

                    elif sprite[0].id == "general-menu-btn":
                        self.clear_groups()
                        self.parent.pushState(
                            menugeneral.Screen(self.parent, self.is_overlay)
                        )
        self.handle_magnifier(events)

    def update(self):
        """Update cursor position, magnifier, and button tooltips."""
        self.mouse.update()
        self.magnifier.magnificar(self.parent.screen)
        self.button_group.update(self.tooltip_group)
