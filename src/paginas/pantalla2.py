#!/usr/bin/env python

import pygame

from librerias import pantalla
from librerias.popups import PopUp

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


class estado(pantalla.Pantalla):
    def __init__(self, parent):
        """
        Método inicializador de la clase.

        @param parent: Instancia del gestor de pantallas.
        @type parent: Manejador
        """

        self.name = "screen_2"
        super().__init__(parent, self.name)

        self.load_images(images)

        self.dic_img = {"F1": self.f1}

        self.load_banners(banners)
        self.load_buttons(buttons)
        self.cargar_textos()

        # Initialize scene
        self.resume()

    # def show_instructions(self):
    #     """
    #     Muestra las instrucciones de uso de la pantalla actual.
    #     """
    #     if not self.popup_ins.activo:
    #         self.popup_ins.agregar_grupo()
    #         self.spserver.processtext(
    #             self.parent.text_content["popups"][self.name]["reader_1"],
    #             self.parent.config.is_screen_reader_enabled(),
    #         )

    #     else:
    #         self.popup_ins.eliminar_grupo()
    #         self.spserver.stopserver()

    def cargar_textos(self):
        """
        Carga los textos utilizados en esta pantalla.
        """
        pass
        # self.popup_ins = PopUp(
        #     self.parent,
        #     self.parent.text_content["popups"][self.name]["text_1"],
        #     "",
        #     self.dic_img,
        #     self.grupo_popup,
        #     2,
        #     512,
        #     265,
        #     100,
        # )

    def resume(self):
        """
        Verifica si es la primera vez que se muestra esta pantalla. Carga los objetos correspondientes
        según el caso.
        """
        self.parent.primera_vez = False
        if self.parent.config.get_preference("texto_cambio", True):
            self.load_buttons(buttons)
            self.cargar_textos()
            self.parent.config.set_preference("texto_cambio", False)

        if self.parent.config.has_visited_screen("p2"):
            self.parent.config.mark_screen_visited("p2")
            # self.show_instructions()
        else:
            self.spserver.processtext(
                "Menú del Recurso", self.parent.config.is_screen_reader_enabled()
            )

        self.grupo_banner.add(self.banner_inf)
        self.grupo_botones.add(
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
        Evalúa los eventos que se generan en esta pantalla.

        @param events: Lista de los eventos.
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
                self.chequeo_botones(self.grupo_botones)
                self.numero_elementos = len(self.lista_botones)
                self.lista_final = self.lista_botones

                if event.key == pygame.K_RIGHT:
                    self.controlador_lector_evento_K_RIGHT()
                    self.deteccion_movimiento = True

                elif event.key == pygame.K_LEFT:
                    self.controlador_lector_evento_K_LEFT()

                elif self.deteccion_movimiento:
                    if event.key == pygame.K_RETURN:
                        if self.x.tipo_objeto == "boton":

                            if self.x.id == "plantas":
                                self.limpiar_grupos()
                                self.parent.changeState(pantalla3.estado(self.parent))

                            elif self.x.id == "agri":
                                self.limpiar_grupos()
                                self.parent.changeState(pantalla8.estado(self.parent))

                            elif self.x.id == "act1":
                                self.limpiar_grupos()
                                self.parent.pushState(actividad1.estado(self.parent))

                            elif self.x.id == "act2":
                                self.limpiar_grupos()
                                self.parent.pushState(actividad2.actividad(self.parent))

                            elif self.x.id == "repro":
                                self.limpiar_grupos()
                                self.parent.changeState(pantalla5.estado(self.parent))

                            elif self.x.id == "config":
                                self.limpiar_grupos()
                                self.parent.pushState(
                                    menucfg.estado(self.parent, self.previa)
                                )

                            elif self.x.id == "orientacion":
                                self.limpiar_grupos()
                                self.parent.pushState(pantalla11.estado(self.parent))

            # if (
            #     pygame.sprite.spritecollideany(self.raton, self.grupo_botones)
            #     and not self.popup_ins.activo
            # ):
            if (
                pygame.sprite.spritecollideany(self.raton, self.grupo_botones)
            ):
                sprite = pygame.sprite.spritecollide(
                    self.raton, self.grupo_botones, False
                )
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.spserver.stopserver()
                    if sprite[0].id == "orientacion":
                        self.limpiar_grupos()
                        self.parent.pushState(pantalla11.estado(self.parent))
                    elif sprite[0].id == "plantas":
                        self.limpiar_grupos()
                        self.parent.changeState(pantalla3.estado(self.parent))
                    elif sprite[0].id == "repro":
                        self.limpiar_grupos()
                        self.parent.changeState(pantalla5.estado(self.parent))
                    elif sprite[0].id == "agri":
                        self.limpiar_grupos()
                        self.parent.changeState(pantalla8.estado(self.parent))
                    elif sprite[0].id == "config":
                        self.limpiar_grupos()
                        self.parent.pushState(menucfg.estado(self.parent, self.previa))
                    elif sprite[0].id == "act1":
                        self.limpiar_grupos()
                        self.parent.pushState(actividad1.estado(self.parent))
                    elif sprite[0].id == "act2":
                        self.limpiar_grupos()
                        self.parent.pushState(actividad2.actividad(self.parent))
        self.minimag(events)

    def update(self):
        """
        Actualiza la posición del cursor, el magnificador de pantalla en caso de que este activado y los
        tooltip de los botones.
        """
        self.raton.update()
        self.obj_magno.magnificar(self.parent.screen)
        self.grupo_botones.update(self.grupo_tooltip)
