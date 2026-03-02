#!/usr/bin/env python
"""Main resource menu screen for the sv2 educational app."""

import pygame

from components import screen
from components.popups import PopUp

from paginas import menucfg
from paginas import pantalla3
from paginas import pantalla5
from paginas import pantalla8
from paginas import pantalla11
from paginas import actividad1
from paginas import actividad2

banners = ["banner-inf"]

buttons = [
    "nino",
    "nina",
    "plantas",
    "repro",
    "agri",
    "config",
    "orientacion",
]

images = ["f1"]


class Screen(screen.Screen):
    """Screen that presents the top-level navigation menu for all content sections."""

    def __init__(self, parent):
        """
        Initialise the main resource menu screen.

        @param parent: Screen manager instance.
        @type parent: Manejador
        """

        self.name = "screen_2"
        super().__init__(parent, self.name)

        self.load_images(images)

        self.dic_img = {"F1": self.f1}

        self.load_banners(banners)
        self.load_buttons(buttons)
        self.load_texts()

    # def show_instructions(self):
    #     """
    #     Muestra las instrucciones de uso de la pantalla actual.
    #     """
    #     if not self.popup_ins.activo:
    #         self.popup_ins.add_to_group()
    #         self.speech_server.processtext(
    #             self.parent.text_content["popups"][self.name]["reader_1"],
    #             self.parent.config.is_screen_reader_enabled(),
    #         )

    #     else:
    #         self.popup_ins.remove_from_group()
    #         self.speech_server.stopserver()

    def load_texts(self):
        """Load text objects used on this screen."""
        pass
        # self.popup_ins = PopUp(
        #     self.parent,
        #     self.parent.text_content["popups"][self.name]["text_1"],
        #     "",
        #     self.dic_img,
        #     self.popup_group,
        #     2,
        #     512,
        #     265,
        #     100,
        # )

    def start(self):
        self.resume()

    def resume(self):
        """Reload buttons and texts if config changed, then populate sprite groups."""
        self.parent.first_run = False
        if self.parent.config.get_preference("texto_cambio", True):
            self.load_buttons(buttons)
            self.load_texts()
            self.parent.config.set_preference("texto_cambio", False)

        if self.parent.config.has_visited_screen("p2"):
            self.parent.config.mark_screen_visited("p2")
            # self.show_instructions()
        else:
            self.speech_server.processtext(
                "Menú del Recurso", self.parent.config.is_screen_reader_enabled()
            )

        self.banner_group.add(self.banner_inf)
        self.button_group.add(
            self.plantas,
            self.repro,
            self.agri,
            self.nino,
            self.nina,
            self.config,
            self.orientacion,
        )
        pygame.display.set_caption("Sembrando para el futuro")

    def handleEvents(self, events):
        """
        Process input events for this screen.

        @param events: Event list from the main loop.
        @type events: list
        """
        for event in events:
            self.teclasPulsadas = pygame.key.get_pressed()
            if event.type == pygame.QUIT:
                self.parent.quit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                pass
                # self.show_instructions()

            # if event.type == pygame.KEYDOWN and not self.popup_ins.activo:
            if event.type == pygame.KEYDOWN:
                self.collect_buttons(self.button_group)
                self.element_count = len(self.button_list)
                self.nav_list = self.button_list

                if event.key == pygame.K_RIGHT:
                    self.nav_right()
                    self.keyboard_nav_active = True

                elif event.key == pygame.K_LEFT:
                    self.nav_left()

                elif self.keyboard_nav_active:
                    if event.key == pygame.K_RETURN:
                        if self.x.obj_type == "button":

                            if self.x.id == "plantas":
                                self.clear_groups()
                                self.parent.changeState(pantalla3.Screen(self.parent))

                            elif self.x.id == "agri":
                                self.clear_groups()
                                self.parent.changeState(pantalla8.Screen(self.parent))

                            elif self.x.id == "act1":
                                self.clear_groups()
                                self.parent.pushState(actividad1.Screen(self.parent))

                            elif self.x.id == "act2":
                                self.clear_groups()
                                self.parent.pushState(actividad2.actividad(self.parent))

                            elif self.x.id == "repro":
                                self.clear_groups()
                                self.parent.changeState(pantalla5.Screen(self.parent))

                            elif self.x.id == "config":
                                self.clear_groups()
                                self.parent.pushState(
                                    menucfg.Screen(self.parent, self.is_overlay)
                                )

                            elif self.x.id == "orientacion":
                                self.clear_groups()
                                self.parent.pushState(pantalla11.Screen(self.parent))

            # if (
            #     pygame.sprite.spritecollideany(self.mouse, self.button_group)
            #     and not self.popup_ins.activo
            # ):
            if (
                pygame.sprite.spritecollideany(self.mouse, self.button_group)
            ):
                sprite = pygame.sprite.spritecollide(
                    self.mouse, self.button_group, False
                )
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.speech_server.stopserver()
                    if sprite[0].id == "orientacion":
                        self.clear_groups()
                        self.parent.pushState(pantalla11.Screen(self.parent))
                    elif sprite[0].id == "plantas":
                        self.clear_groups()
                        self.parent.changeState(pantalla3.Screen(self.parent))
                    elif sprite[0].id == "repro":
                        self.clear_groups()
                        self.parent.changeState(pantalla5.Screen(self.parent))
                    elif sprite[0].id == "agri":
                        self.clear_groups()
                        self.parent.changeState(pantalla8.Screen(self.parent))
                    elif sprite[0].id == "config":
                        self.clear_groups()
                        self.parent.pushState(menucfg.Screen(self.parent, self.is_overlay))
                    elif sprite[0].id == "act1":
                        self.clear_groups()
                        self.parent.pushState(actividad1.Screen(self.parent))
                    elif sprite[0].id == "act2":
                        self.clear_groups()
                        self.parent.pushState(actividad2.actividad(self.parent))
        self.handle_magnifier(events)

    def update(self):
        """Update cursor position, magnifier, and button tooltips."""
        self.mouse.update()
        self.magnifier.magnificar(self.parent.screen)
        self.button_group.update(self.tooltip_group)
