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

        self.button_actions = {
            "plantas":     self.go_plantas,
            "repro":       self.go_repro,
            "agri":        self.go_agri,
            "config":      self.go_config,
            "orientacion": self.go_orientacion,
        }

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
        if self.parent.config.is_text_change_enabled():
            self.load_buttons(buttons)
            self.load_texts()
            self.parent.config.set_text_change_enabled(False)

        if not self.parent.config.has_visited_screen("p2"):
            self.parent.config.mark_screen_visited("p2")
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

    def go_plantas(self):
        self.clear_groups()
        self.parent.changeState(pantalla3.Screen(self.parent))

    def go_repro(self):
        self.clear_groups()
        self.parent.changeState(pantalla5.Screen(self.parent))

    def go_agri(self):
        self.clear_groups()
        self.parent.changeState(pantalla8.Screen(self.parent))

    def go_config(self):
        self.clear_groups()
        self.parent.pushState(menucfg.Screen(self.parent, self.is_overlay))

    def go_orientacion(self):
        self.clear_groups()
        self.parent.pushState(pantalla11.Screen(self.parent))

    def go_act1(self):
        self.clear_groups()
        self.parent.pushState(actividad1.Screen(self.parent))

    def go_act2(self):
        self.clear_groups()
        self.parent.pushState(actividad2.actividad(self.parent))

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

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.sprite.spritecollideany(self.mouse, self.button_group):
                    sprite = pygame.sprite.spritecollide(self.mouse, self.button_group, False)
                    self.speech_server.stopserver()
                    self.button_actions.get(sprite[0].id, lambda: None)()

        self._rebuild_nav()
        self.handle_magnifier(events)
