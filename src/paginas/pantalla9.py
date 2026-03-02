#!/usr/bin/env python
"""Interactive map screen showing agricultural regions of Venezuela (screen 9)."""

import pygame

from components import screen
from components.texto import Text
from components.popups import PopUp
from components.background import Background
from components.pixelperfect import *
from components.objmask import object_mask

from paginas import menucfg
from paginas import pantalla2
from paginas import pantalla8
from paginas import pantalla10

banners = [
    "banner-inf",
    "banner-siembra",
]

buttons = [
    "home",
    "back",
    "config",
]


class Screen(screen.Screen):
    """Screen displaying a pixel-perfect clickable map of Venezuela's agricultural regions."""

    def __init__(self, parent):
        """
        Initialise the screen and build all map region mask objects.

        @param parent: Screen manager instance.
        @type parent: Manejador
        """

        self.name = "screen_9"
        super().__init__(parent, self.name)

        self.fondo_texto = False

        self.mouse = object_mask("Cursor", 850, 512, self.misc_path + "puntero.png")
        # Para mantener las piezas del mapa bien ubicadas no se deben modificar los valores x e y de las regiones, solo de zulia.
        self.zulia = object_mask(
            "región zuliana",
            13,
            140,
            self.misc_path + "zulia-des.png",
            self.misc_path + "zulia-act.png",
        )
        self.occ = object_mask(
            "región occidental",
            self.zulia.rect.left + 55,
            self.zulia.rect.top - 6,
            self.misc_path + "occ-des.png",
            self.misc_path + "occ-act.png",
        )
        self.central = object_mask(
            "región central",
            self.zulia.rect.left + 115,
            self.zulia.rect.top + 37,
            self.misc_path + "central-des.png",
            self.misc_path + "central-act.png",
        )
        self.capital = object_mask(
            "región capital",
            self.zulia.rect.left + 152,
            self.zulia.rect.top + 32,
            self.misc_path + "capital-des.png",
            self.misc_path + "capital-act.png",
        )
        self.ori = object_mask(
            "región nor oriental",
            self.zulia.rect.left + 195,
            self.zulia.rect.top + 29,
            self.misc_path + "ori-des.png",
            self.misc_path + "ori-act.png",
        )
        self.andes = object_mask(
            "región los andes",
            self.zulia.rect.left + 23,
            self.zulia.rect.top + 48,
            self.misc_path + "andes-des.png",
            self.misc_path + "andes-act.png",
        )
        self.llanos = object_mask(
            "región los llanos",
            self.zulia.rect.left + 26,
            self.zulia.rect.top + 47,
            self.misc_path + "llanos-des.png",
            self.misc_path + "llanos-act.png",
        )
        self.guayana = object_mask(
            "región guayana",
            self.zulia.rect.left + 140,
            self.zulia.rect.top + 48,
            self.misc_path + "guayana-des.png",
            self.misc_path + "guayana-act.png",
        )
        self.insu = object_mask(
            "región insular",
            self.zulia.rect.left + 149,
            self.zulia.rect.top - 6,
            self.misc_path + "insular-des.png",
            self.misc_path + "insular-act.png",
        )

        self.limites1 = pygame.image.load(self.misc_path + "limitemar.png").convert_alpha()
        self.limites2 = pygame.image.load(
            self.misc_path + "limitemar2.png"
        ).convert_alpha()
        self.zona_r = pygame.image.load(self.misc_path + "zona-recla.png").convert_alpha()
        self.n_estados = pygame.image.load(
            self.misc_path + "nombre-estados.png"
        ).convert_alpha()

        self.load_banners(banners)
        self.load_buttons(buttons)
        self.load_texts()
        self.bg = background(573, 377)

    def load_texts(self):
        """Load and build the text objects for all map regions and the introductory popup."""
        self.texto9_2_1 = Text(
            490,
            60,
            self.screen_text("text_2_1"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_2_2 = Text(
            490,
            self.texto9_2_1.y + self.texto9_2_1.total_width + 10,
            self.screen_text("text_2_2"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_2_3 = Text(
            490,
            self.texto9_2_2.y + self.texto9_2_2.total_width + 10,
            self.screen_text("text_2_3"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_2_4 = Text(
            490,
            self.texto9_2_3.y + self.texto9_2_3.total_width + 10,
            self.screen_text("text_2_4"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )

        self.texto9_3_1 = Text(
            490,
            60,
            self.screen_text("text_3_1"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_3_2 = Text(
            490,
            self.texto9_3_1.y + self.texto9_3_1.total_width + 10,
            self.screen_text("text_3_2"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_3_3 = Text(
            490,
            self.texto9_3_2.y + self.texto9_3_2.total_width + 10,
            self.screen_text("text_3_3"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )

        self.texto9_4_1 = Text(
            490,
            60,
            self.screen_text("text_4_1"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_4_2 = Text(
            490,
            self.texto9_4_1.y + self.texto9_4_1.total_width + 10,
            self.screen_text("text_4_2"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_4_3 = Text(
            490,
            self.texto9_4_2.y + self.texto9_4_2.total_width + 10,
            self.screen_text("text_4_3"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )

        self.texto9_5_1 = Text(
            490,
            60,
            self.screen_text("text_5_1"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_5_2 = Text(
            490,
            self.texto9_5_1.y + self.texto9_5_1.total_width + 10,
            self.screen_text("text_5_2"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_5_3 = Text(
            490,
            self.texto9_5_2.y + self.texto9_5_2.total_width + 10,
            self.screen_text("text_5_3"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_6_1 = Text(
            490,
            60,
            self.screen_text("text_6_1"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_6_2 = Text(
            490,
            self.texto9_6_1.y + self.texto9_6_1.total_width + 10,
            self.screen_text("text_6_2"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_6_3 = Text(
            490,
            self.texto9_6_2.y + self.texto9_6_2.total_width + 10,
            self.screen_text("text_6_3"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )

        self.texto9_7_1 = Text(
            490,
            60,
            self.screen_text("text_7_1"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_7_2 = Text(
            490,
            self.texto9_7_1.y + self.texto9_7_1.total_width + 10,
            self.screen_text("text_7_2"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_7_3 = Text(
            490,
            self.texto9_7_2.y + self.texto9_7_2.total_width + 10,
            self.screen_text("text_7_3"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )

        self.texto9_8_1 = Text(
            490,
            60,
            self.screen_text("text_8_1"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_8_2 = Text(
            490,
            self.texto9_8_1.y + self.texto9_8_1.total_width + 10,
            self.screen_text("text_8_2"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_8_3 = Text(
            490,
            self.texto9_8_2.y + self.texto9_8_2.total_width + 10,
            self.screen_text("text_8_3"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )

        self.texto9_9_1 = Text(
            490,
            60,
            self.screen_text("text_9_1"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_9_2 = Text(
            490,
            self.texto9_9_1.y + self.texto9_9_1.total_width + 10,
            self.screen_text("text_9_2"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_9_3 = Text(
            490,
            self.texto9_9_2.y + self.texto9_9_2.total_width + 10,
            self.screen_text("text_9_3"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )

        self.texto9_10_1 = Text(
            490,
            60,
            self.screen_text("text_10_1"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_10_2 = Text(
            490,
            self.texto9_10_1.y + self.texto9_10_1.total_width + 10,
            self.screen_text("text_10_2"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_10_3 = Text(
            490,
            self.texto9_10_2.y + self.texto9_10_2.total_width + 10,
            self.screen_text("text_10_3"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )
        self.texto9_10_4 = Text(
            490,
            self.texto9_10_3.y + self.texto9_10_3.total_width + 10,
            self.screen_text("text_10_4"),
            self.parent.config.get_font_size(),
            1,
            1000,
        )

        self.popup_ins1 = PopUp(
            self.parent,
            (self.parent.text_loader.popup("screen_9", "text_1"),),
            "",
            None,
            self.popup_group,
            1,
            750,
            400,
            -100,
        )
        self.popup_ins1.add_to_group()

    def start(self):
        self.resume()

    def resume(self):
        """Reload buttons and texts if config changed, reset all map regions, then populate sprite groups."""
        if self.parent.config.is_text_change_enabled():
            self.load_buttons(buttons)
            self.load_texts()
            self.parent.config.set_text_change_enabled(False)
        self.popup_ins1.add_to_group()
        self.capital.apagar()
        self.ori.apagar()
        self.zulia.apagar()
        self.occ.apagar()
        self.andes.apagar()
        self.llanos.apagar()
        self.central.apagar()
        self.guayana.apagar()
        self.banner_group.add(self.banner_siembra, self.banner_inf)
        self.button_group.add(self.config, self.back, self.home)
        self.map_group.add(
            self.zulia,
            self.occ,
            self.central,
            self.insu,
            self.capital,
            self.ori,
            self.andes,
            self.llanos,
            self.guayana,
        )
        self.speech_server.processtext(
            "Pantalla: La Agricultura en Venezuela: ", self.parent.config.is_screen_reader_enabled()
        )
        self.speech_server.processtext(
            self.parent.text_loader.popup("screen_9", "reader_1"),
            self.parent.config.is_screen_reader_enabled(),
        )

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
                self.collect_masks(self.map_group)
                self.collect_buttons(self.button_group)
                self.nav_list = (
                    self.word_list + self.mask_list + self.button_list
                )
                self.element_count = len(self.nav_list)

                if event.key == pygame.K_RIGHT:
                    self.fondo_texto = False
                    self.word_group.empty()
                    self.keyboard_nav_active = True
                    self.nav_right()

                elif event.key == pygame.K_LEFT:
                    self.fondo_texto = False
                    self.word_group.empty()
                    self.nav_left()

                if self.keyboard_nav_active:
                    if event.key == pygame.K_RETURN:
                        if self.x.obj_type == "map":
                            self.fondo_texto = True

                            if self.x.id == "región capital":
                                self.word_group.empty()
                                self.central.apagar()
                                self.llanos.apagar()
                                self.zulia.apagar()
                                self.ori.apagar()
                                self.occ.apagar()
                                self.andes.apagar()
                                self.llanos.apagar()
                                self.capital.iluminar()
                                self.insu.apagar()
                                self.word_group.add(
                                    self.texto9_2_1.words,
                                    self.texto9_2_2.words,
                                    self.texto9_2_3.words,
                                    self.texto9_2_4.words,
                                )
                                self.speech_server.processtext(
                                    self.screen_text("text_2_1l")
                                    + self.texto9_2_2.texto
                                    + self.texto9_2_3.texto
                                    + self.texto9_2_4.texto,
                                    self.parent.config.is_screen_reader_enabled(),
                                )

                            elif self.x.id == "región central":
                                self.word_group.empty()
                                self.capital.apagar()
                                self.llanos.apagar()
                                self.zulia.apagar()
                                self.ori.apagar()
                                self.occ.apagar()
                                self.andes.apagar()
                                self.llanos.apagar()
                                self.central.iluminar()
                                self.insu.apagar()
                                self.word_group.add(
                                    self.texto9_3_1.words,
                                    self.texto9_3_2.words,
                                    self.texto9_3_3.words,
                                )
                                self.speech_server.processtext(
                                    self.screen_text("text_3_1l")
                                    + self.texto9_3_2.texto
                                    + self.texto9_3_3.texto,
                                    self.parent.config.is_screen_reader_enabled(),
                                )

                            if self.x.id == "región los llanos":
                                self.word_group.empty()
                                self.capital.apagar()
                                self.central.apagar()
                                self.ori.apagar()
                                self.zulia.apagar()
                                self.occ.apagar()
                                self.andes.apagar()
                                self.llanos.iluminar()
                                self.insu.apagar()
                                self.word_group.add(
                                    self.texto9_4_1.words,
                                    self.texto9_4_2.words,
                                    self.texto9_4_3.words,
                                )
                                self.speech_server.processtext(
                                    self.screen_text("text_4_1l")
                                    + self.texto9_4_2.texto
                                    + self.texto9_4_3.texto,
                                    self.parent.config.is_screen_reader_enabled(),
                                )

                            if self.x.id == "región occidental":
                                self.word_group.empty()
                                self.capital.apagar()
                                self.llanos.apagar()
                                self.central.apagar()
                                self.ori.apagar()
                                self.zulia.apagar()
                                self.andes.apagar()
                                self.occ.iluminar()
                                self.llanos.apagar()
                                self.guayana.apagar()
                                self.insu.apagar()
                                self.word_group.add(
                                    self.texto9_5_1.words,
                                    self.texto9_5_2.words,
                                    self.texto9_5_3.words,
                                )
                                self.speech_server.processtext(
                                    self.screen_text("text_5_1l")
                                    + self.texto9_5_2.texto
                                    + self.texto9_5_3.texto,
                                    self.parent.config.is_screen_reader_enabled(),
                                )

                            if self.x.id == "región zuliana":
                                self.word_group.empty()
                                self.capital.apagar()
                                self.llanos.apagar()
                                self.central.apagar()
                                self.ori.apagar()
                                self.zulia.iluminar()
                                self.occ.apagar()
                                self.andes.apagar()
                                self.llanos.apagar()
                                self.guayana.apagar()
                                self.insu.apagar()
                                self.word_group.add(
                                    self.texto9_6_1.words,
                                    self.texto9_6_2.words,
                                    self.texto9_6_3.words,
                                )
                                self.speech_server.processtext(
                                    self.screen_text("text_6_1l")
                                    + self.texto9_6_2.texto
                                    + self.texto9_6_3.texto,
                                    self.parent.config.is_screen_reader_enabled(),
                                )

                            if self.x.id == "región los andes":
                                self.word_group.empty()
                                self.capital.apagar()
                                self.llanos.apagar()
                                self.central.apagar()
                                self.zulia.apagar()
                                self.ori.apagar()
                                self.occ.apagar()
                                self.andes.iluminar()
                                self.llanos.apagar()
                                self.guayana.apagar()
                                self.insu.apagar()
                                self.word_group.add(
                                    self.texto9_7_1.words,
                                    self.texto9_7_2.words,
                                    self.texto9_7_3.words,
                                )
                                self.speech_server.processtext(
                                    self.screen_text("text_7_1l")
                                    + self.texto9_7_2.texto
                                    + self.texto9_7_3.texto,
                                    self.parent.config.is_screen_reader_enabled(),
                                )

                            if self.x.id == "región nor oriental":
                                self.word_group.empty()
                                self.capital.apagar()
                                self.llanos.apagar()
                                self.central.apagar()
                                self.ori.iluminar()
                                self.zulia.apagar()
                                self.occ.apagar()
                                self.andes.apagar()
                                self.guayana.apagar()
                                self.insu.apagar()
                                self.word_group.add(
                                    self.texto9_8_1.words,
                                    self.texto9_8_2.words,
                                    self.texto9_8_3.words,
                                )
                                self.speech_server.processtext(
                                    self.screen_text("text_8_1l")
                                    + self.texto9_8_2.texto
                                    + self.texto9_8_3.texto,
                                    self.parent.config.is_screen_reader_enabled(),
                                )

                            if self.x.id == "región guayana":
                                self.word_group.empty()
                                self.capital.apagar()
                                self.llanos.apagar()
                                self.central.apagar()
                                self.ori.apagar()
                                self.occ.apagar()
                                self.zulia.apagar()
                                self.andes.apagar()
                                self.llanos.apagar()
                                self.insu.apagar()
                                self.guayana.iluminar()
                                self.word_group.add(
                                    self.texto9_9_1.words,
                                    self.texto9_9_2.words,
                                    self.texto9_9_3.words,
                                )
                                self.speech_server.processtext(
                                    self.screen_text("text_9_1l")
                                    + self.texto9_9_2.texto
                                    + self.texto9_9_3.texto,
                                    self.parent.config.is_screen_reader_enabled(),
                                )

                            if self.x.id == "región insular":
                                self.word_group.empty()
                                self.capital.apagar()
                                self.llanos.apagar()
                                self.central.apagar()
                                self.ori.apagar()
                                self.occ.apagar()
                                self.zulia.apagar()
                                self.andes.apagar()
                                self.llanos.apagar()
                                self.guayana.apagar()
                                self.insu.iluminar()
                                self.word_group.add(
                                    self.texto9_10_1.words,
                                    self.texto9_10_2.words,
                                    self.texto9_10_3.words,
                                    self.texto9_10_4.words,
                                )
                                self.speech_server.processtext(
                                    self.screen_text("text_10_1l")
                                    + self.texto9_10_2.texto
                                    + self.texto9_10_3.texto
                                    + self.texto9_10_4.texto,
                                    self.parent.config.is_screen_reader_enabled(),
                                )

                        elif self.x.obj_type == "button":
                            if self.x.id == "back":
                                self.clear_groups()
                                self.parent.animation_index = 3
                                self.parent.changeState(
                                    pantalla8.Screen(self.parent, 3)
                                )

                            elif self.x.id == "config":
                                self.clear_groups()
                                self.parent.pushState(
                                    menucfg.Screen(self.parent, self.is_overlay)
                                )

                            elif self.x.id == "home":
                                self.clear_groups()
                                self.parent.changeState(pantalla2.Screen(self.parent))

            lista = spritecollide_pp(self.mouse, self.map_group)
            if not lista == []:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.keyboard_nav_active = False
                    self.fondo_texto = True
                    if lista[0].id == "región capital":
                        self.central.apagar()
                        self.llanos.apagar()
                        self.ori.apagar()
                        self.occ.apagar()
                        self.zulia.apagar()
                        self.andes.apagar()
                        self.llanos.apagar()
                        self.capital.iluminar()
                        self.insu.apagar()
                        self.word_group.empty()
                        self.word_group.add(
                            self.texto9_2_1.words,
                            self.texto9_2_2.words,
                            self.texto9_2_3.words,
                            self.texto9_2_4.words,
                        )

                    if lista[0].id == "región central":
                        self.capital.apagar()
                        self.llanos.apagar()
                        self.ori.apagar()
                        self.occ.apagar()
                        self.zulia.apagar()
                        self.andes.apagar()
                        self.llanos.apagar()
                        self.central.iluminar()
                        self.insu.apagar()
                        self.word_group.empty()
                        self.word_group.add(
                            self.texto9_3_1.words,
                            self.texto9_3_2.words,
                            self.texto9_3_3.words,
                        )

                    if lista[0].id == "región los llanos":
                        self.capital.apagar()
                        self.central.apagar()
                        self.llanos.iluminar()
                        self.zulia.apagar()
                        self.ori.apagar()
                        self.occ.apagar()
                        self.andes.apagar()
                        self.insu.apagar()
                        self.word_group.empty()
                        self.word_group.add(
                            self.texto9_4_1.words,
                            self.texto9_4_2.words,
                            self.texto9_4_3.words,
                        )

                    if lista[0].id == "región occidental":
                        self.capital.apagar()
                        self.llanos.apagar()
                        self.ori.apagar()
                        self.central.apagar()
                        self.zulia.apagar()
                        self.occ.iluminar()
                        self.llanos.apagar()
                        self.guayana.apagar()
                        self.andes.apagar()
                        self.insu.apagar()
                        self.word_group.empty()
                        self.word_group.add(
                            self.texto9_5_1.words,
                            self.texto9_5_2.words,
                            self.texto9_5_3.words,
                        )

                    if lista[0].id == "región zuliana":
                        self.capital.apagar()
                        self.llanos.apagar()
                        self.central.apagar()
                        self.ori.apagar()
                        self.zulia.iluminar()
                        self.occ.apagar()
                        self.andes.apagar()
                        self.llanos.apagar()
                        self.guayana.apagar()
                        self.insu.apagar()
                        self.word_group.empty()
                        self.word_group.add(
                            self.texto9_6_1.words,
                            self.texto9_6_2.words,
                            self.texto9_6_3.words,
                        )

                    if lista[0].id == "región los andes":
                        self.capital.apagar()
                        self.llanos.apagar()
                        self.central.apagar()
                        self.guayana.apagar()
                        self.zulia.apagar()
                        self.ori.apagar()
                        self.occ.apagar()
                        self.andes.iluminar()
                        self.llanos.apagar()
                        self.insu.apagar()
                        self.word_group.empty()
                        self.word_group.add(
                            self.texto9_7_1.words,
                            self.texto9_7_2.words,
                            self.texto9_7_3.words,
                        )

                    if lista[0].id == "región nor oriental":
                        self.capital.apagar()
                        self.central.apagar()
                        self.ori.iluminar()
                        self.llanos.apagar()
                        self.guayana.apagar()
                        self.zulia.apagar()
                        self.occ.apagar()
                        self.andes.apagar()
                        self.insu.apagar()
                        self.word_group.empty()
                        self.word_group.add(
                            self.texto9_8_1.words,
                            self.texto9_8_2.words,
                            self.texto9_8_3.words,
                        )

                    if lista[0].id == "región guayana":
                        self.capital.apagar()
                        self.llanos.apagar()
                        self.central.apagar()
                        self.ori.apagar()
                        self.zulia.apagar()
                        self.occ.apagar()
                        self.andes.apagar()
                        self.guayana.iluminar()
                        self.insu.apagar()
                        self.word_group.empty()
                        self.word_group.add(
                            self.texto9_9_1.words,
                            self.texto9_9_2.words,
                            self.texto9_9_3.words,
                        )

                    if lista[0].id == "región insular":
                        self.capital.apagar()
                        self.llanos.apagar()
                        self.central.apagar()
                        self.ori.apagar()
                        self.zulia.apagar()
                        self.occ.apagar()
                        self.andes.apagar()
                        self.guayana.apagar()
                        self.insu.iluminar()
                        self.word_group.empty()
                        self.word_group.add(
                            self.texto9_10_1.words,
                            self.texto9_10_2.words,
                            self.texto9_10_3.words,
                            self.texto9_10_4.words,
                        )

            elif not self.keyboard_nav_active:
                self.fondo_texto = False
                self.capital.apagar()
                self.central.apagar()
                self.guayana.apagar()
                self.andes.apagar()
                self.zulia.apagar()
                self.occ.apagar()
                self.ori.apagar()
                self.llanos.apagar()
                self.word_group.empty()
                self.text_bg_group.empty()

            if pygame.sprite.spritecollideany(self.mouse, self.button_group):
                sprite = pygame.sprite.spritecollide(
                    self.mouse, self.button_group, False
                )
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if sprite[0].id == "back":
                        self.clear_groups()
                        self.parent.animation_index = 3
                        self.parent.changeState(pantalla8.Screen(self.parent, 3))

                    elif sprite[0].id == "config":
                        self.clear_groups()
                        self.parent.pushState(menucfg.Screen(self.parent, self.is_overlay))

                    elif sprite[0].id == "home":
                        self.clear_groups()
                        self.parent.changeState(pantalla2.Screen(self.parent))
        self.handle_magnifier(events)

    def update(self):
        """Update cursor position, magnifier, button tooltips, and sync the pixel-perfect mouse mask to the pointer."""
        self.mouse.update()
        self.magnifier.magnificar(self.parent.screen)
        self.button_group.update(self.tooltip_group)
        self.mouse.rect.center = pygame.mouse.get_pos()

    def draw(self):
        """Draw the background, map layers, region sprites, and text panel onto the screen manager surface."""

        self.parent.screen.blit(self.background, (0, 0))
        self.banner_group.draw(self.parent.screen)
        self.parent.screen.blit(self.zona_r, (320, 233))
        self.parent.screen.blit(self.limites1, (50, 60))
        self.parent.screen.blit(self.limites2, (305, 145))
        self.map_group.draw(self.parent.screen)
        self.popup_group.draw(self.parent.screen)
        if self.fondo_texto:
            self.parent.screen.blit(self.bg.img, (451, 55))
        self.button_group.draw(self.parent.screen)
        self.text_bg_group.draw(self.parent.screen)
        self.word_group.draw(self.parent.screen)
        self.tooltip_group.draw(self.parent.screen)
        self.parent.screen.blit(self.n_estados, (40, 95))
        if self.parent.magnifier_active:
            self.magnifier_group.draw(self.parent.screen, self.enable)
        if self.keyboard_nav_active:
            self.draw_focus_rect()
        self.draw_debug_rectangles()

    def go_to_glossary(self):
        self.parent.pushState(pantalla10.Screen(self.parent))
