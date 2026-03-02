#!/usr/bin/env python

import pygame

from components import screen
from components.texto import Text
from components.popups import PopUp
from paginas import pantalla2

banners = [
    "banner-inf",
    "banner-acc-visual",
]

buttons = [
    "puerta",
    "guardar",
    "onmag",
    "onmag_si",
    "offmag",
    "offmag_si",
    "tam18",
    "tam18_sel",
    "tam20",
    "tam20_sel",
    "tam22",
    "tam22_sel",
    "lector",
    "lector_si",
    "oflector",
    "oflector_si",
    "vbaja",
    "vbaja_sel",
    "vmedia",
    "vmedia_sel",
    "vrapida",
    "vrapida_sel",
]


class Screen(screen.Screen):
    """Visual accessibility configuration screen for magnifier, font size, and screen-reader settings."""

    def __init__(self, parent, is_overlay=False):
        """
        Initialise the screen.

        @param parent: Screen manager instance.
        @type parent: Manejador
        @param is_overlay: True if this screen is pushed over another; False if loaded via changeState.
        @type is_overlay: bool
        """
        self.name = "screen_vis"
        self.parent = parent
        self.is_overlay = is_overlay
        super().__init__(parent, self.name)

        # Botones magnificador
        self.img1 = pygame.image.load(self.popups_path + "f5.png").convert_alpha()
        self.img2 = pygame.image.load(self.popups_path + "mas.png").convert_alpha()
        self.img3 = pygame.image.load(self.popups_path + "menos.png").convert_alpha()
        cont_img = {"F5": self.img1, "MAS": self.img2, "MENOS": self.img3}

        self.popup_mag = PopUp(
            parent,
            self.parent.text_loader.popup("screen_1_reader", "text_magnifier"),
            "",
            cont_img,
            self.popup_group,
            2,
            730,
            230,
            -50,
        )

        # Configuracion accesibilidad visual textos
        self.q1_label = Text(
            10,
            70,
            self.parent.text_loader.ui("config_screens", "visual", "q1_magnifier"),
            20,
            1,
            400,
        )
        self.q1_options = Text(
            100,
            120,
            self.parent.text_loader.ui("config_screens", "visual", "opt_yes_no"),
            20,
            1,
            500,
        )
        self.q3_label = Text(
            10,
            250,
            self.parent.text_loader.ui("config_screens", "visual", "q3_screen_reader"),
            20,
            1,
            400,
        )
        self.q3_options = Text(
            100,
            300,
            self.parent.text_loader.ui("config_screens", "visual", "opt_yes_no"),
            20,
            1,
            500,
        )
        self.q4_label = Text(
            10,
            340,
            self.parent.text_loader.ui("config_screens", "visual", "q4_reader_speed"),
            20,
            1,
            400,
        )
        self.q4_options = Text(
            40,
            390,
            self.parent.text_loader.ui("config_screens", "visual", "opt_reader_speeds"),
            20,
            1,
            500,
        )
        self.save_hint_label = Text(
            200,
            400,
            self.parent.text_loader.ui("config_screens", "visual", "save_hint"),
            20,
            1,
            500,
        )
        self.q2_label = Text(
            10,
            160,
            self.parent.text_loader.ui("config_screens", "visual", "q2_font_size"),
            20,
            1,
            400,
        )
        self.q2_options = Text(
            100,
            200,
            self.parent.text_loader.ui("config_screens", "visual", "opt_font_sizes"),
            20,
            1,
            400,
        )
        instrucciones = self.parent.text_loader.ui(
            "config_screens", "visual", "reader_instructions"
        )
        self.reader_prompt1 = self.parent.text_loader.ui("config_screens", "visual", "reader_q1")
        self.reader_prompt2 = self.parent.text_loader.ui("config_screens", "visual", "reader_q2")

        self.load_banners(banners)
        self.load_buttons(buttons)
        self.load_preferences()
        self.speech_server.stopserver()
        self.opcion = 1
        self.speech_server.processtext(instrucciones + self.reader_prompt1, True)

    def start(self):
        """No-op: initialisation is fully handled in __init__."""
        pass

    def cleanUp(self):
        """No-op: no additional cleanup required."""
        pass

    def pause(self):
        """No-op: screen does not need to pause any state."""
        pass

    def resume(self):
        """No-op: screen does not need to restore any state."""
        pass

    def load_preferences(self):
        """Populate sprite groups from saved preferences, or fall back to defaults if no configuration exists."""
        self.word_group.add(
            self.q1_label.words,
            self.q1_options.words,
            self.q3_label.words,
            self.q3_options.words,
            self.q2_label.words,
            self.q2_options.words,
        )
        self.banner_group.add(self.banner_acc_visual, self.banner_inf)
        if self.parent.config.get_preference("cache", False) == True:
            self.button_group.add(self.puerta)
            if self.parent.config.is_magnifier_enabled():
                self.button_group.add(self.onmag_si, self.offmag)
                self.popup_mag.add_to_group()
            else:
                self.button_group.add(self.onmag, self.offmag_si)
                self.popup_mag.remove_from_group()

            if self.parent.config.get_font_size() == 18:
                self.button_group.add(self.tam18_sel, self.tam20, self.tam22)
            elif self.parent.config.get_font_size() == 20:
                self.button_group.add(self.tam18, self.tam20_sel, self.tam22)
            elif self.parent.config.get_font_size() == 22:
                self.button_group.add(self.tam18, self.tam20, self.tam22_sel)

            if self.parent.config.is_screen_reader_enabled():
                self.button_group.add(self.lector_si, self.oflector)
                self.word_group.add(
                    self.q4_label.words, self.q4_options.words
                )
                if self.parent.config.get_preference("synvel", "baja") == "baja":
                    self.button_group.add(self.vbaja_sel, self.vmedia, self.vrapida)
                elif self.parent.config.get_preference("synvel", "baja") == "media":
                    self.button_group.add(self.vbaja, self.vmedia_sel, self.vrapida)
                elif self.parent.config.get_preference("synvel", "baja") == "rapida":
                    self.button_group.add(self.vbaja, self.vmedia, self.vrapida_sel)
            else:
                self.button_group.add(self.lector, self.oflector_si)
                self.word_group.remove(
                    self.q4_label.words, self.q4_options.words
                )
        else:
            self.button_group.add(
                self.puerta,
                self.onmag,
                self.offmag_si,
                self.tam18_sel,
                self.tam20,
                self.tam22,
                self.lector,
                self.oflector_si,
            )

    def handle_key_input(self, key):
        """
        Advance the screen-reader configuration wizard based on the key pressed.

        @param key: Numeric key code representing the user's selection (1, 2, 3, or 4 for confirm).
        @type key: int
        """
        if self.opcion == 1:
            if key == 1:
                self.speech_server.stopserver()
                self.button_group.remove(self.lector, self.oflector_si, self.guardar)
                self.button_group.add(
                    self.lector_si,
                    self.oflector,
                    self.vbaja_sel,
                    self.vmedia,
                    self.vrapida,
                    self.guardar,
                )
                self.word_group.add(
                    self.q4_label.words, self.q4_options.words
                )
                self.parent.config.set_screen_reader_enabled(True)
                self.speech_server.processtext(self.reader_prompt2, True)
                self.opcion += 1

            elif key == 2:
                self.opcion = 3
                self.button_group.remove(
                    self.lector_si,
                    self.oflector,
                    self.vbaja,
                    self.vbaja_sel,
                    self.vmedia,
                    self.vmedia_sel,
                    self.vrapida,
                    self.vrapida_sel,
                    self.guardar,
                )
                self.word_group.remove(
                    self.q4_label.words, self.q4_options.words
                )
                self.button_group.add(self.lector, self.oflector_si, self.guardar)
                self.parent.config.set_screen_reader_enabled(False)
                self.speech_server.processtext(
                    self.parent.text_loader.ui(
                        "config_screens", "visual", "reader_success"
                    ),
                    True,
                )

        elif self.opcion == 2:
            if key == 1:
                self.button_group.remove(
                    self.vbaja,
                    self.vmedia_sel,
                    self.vrapida,
                    self.vrapida_sel,
                    self.guardar,
                )
                self.button_group.add(
                    self.vbaja_sel, self.vmedia, self.vrapida, self.guardar
                )
                self.parent.config.set_preference("synvel", "baja")

            elif key == 2:
                self.button_group.remove(
                    self.vbaja,
                    self.vbaja_sel,
                    self.vmedia,
                    self.vrapida,
                    self.vrapida_sel,
                    self.guardar,
                )
                self.button_group.add(
                    self.vbaja, self.vmedia_sel, self.vrapida, self.guardar
                )
                self.parent.config.set_preference("synvel", "media")

            elif key == 3:
                self.button_group.remove(
                    self.vbaja,
                    self.vbaja_sel,
                    self.vmedia,
                    self.vmedia_sel,
                    self.vrapida,
                    self.guardar,
                )
                self.button_group.add(
                    self.vbaja, self.vmedia, self.vrapida_sel, self.guardar
                )
                self.parent.config.set_preference("synvel", "rapida")
            self.opcion += 1
            self.speech_server.processtext(
                self.parent.text_loader.ui("config_screens", "visual", "reader_success"),
                True,
            )

        elif self.opcion == 3:
            if key == 4:
                self.parent.config.set_preference("cache", True)
                if (
                    self.parent.config.get_font_size()
                    != self.parent.config.get_preference("t_fuente", 18)
                ):
                    self.parent.set_text_change_enabled(True)
                self.parent.config.flush()
                self.speech_server.update_server()
                self.clear_groups()
                if self.parent.first_run:
                    self.parent.changeState(pantalla2.Screen(self.parent))
                else:
                    if self.is_overlay:
                        self.parent.RETURN_TO_PREV_SCREEN = True
                    self.parent.popState()

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
                if event.key == pygame.K_ESCAPE:
                    self.clear_groups()
                    if self.is_overlay:
                        self.parent.RETURN_TO_PREV_SCREEN = True
                    self.parent.popState()
                elif event.key == 49:
                    self.handle_key_input(1)
                elif event.key == 50:
                    self.handle_key_input(2)
                elif event.key == 51:
                    self.handle_key_input(3)
                elif event.key == pygame.K_RETURN:
                    self.handle_key_input(4)

            if pygame.sprite.spritecollideany(self.mouse, self.button_group):
                sprite = pygame.sprite.spritecollide(
                    self.mouse, self.button_group, False
                )
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    if sprite[0].id == "puerta":
                        self.clear_groups()
                        self.parent.popState()

                    elif sprite[0].id == "tam18":
                        self.button_group.remove(
                            self.tam18, self.tam20_sel, self.tam22_sel
                        )
                        self.button_group.add(
                            self.tam18_sel, self.tam20, self.tam22, self.guardar
                        )
                        self.parent.config.set_preference("t_fuente", 18)

                    elif sprite[0].id == "tam20":
                        self.button_group.remove(
                            self.tam18_sel, self.tam20, self.tam22_sel
                        )
                        self.button_group.add(
                            self.tam18, self.tam20_sel, self.tam22, self.guardar
                        )
                        self.parent.config.set_preference("t_fuente", 20)

                    elif sprite[0].id == "tam22":
                        self.button_group.remove(
                            self.tam18_sel, self.tam20_sel, self.tam22
                        )
                        self.button_group.add(
                            self.tam18, self.tam20, self.tam22_sel, self.guardar
                        )
                        self.parent.config.set_preference("t_fuente", 22)

                    elif sprite[0].id == "onmag":
                        self.button_group.remove(self.onmag, self.offmag_si)
                        self.button_group.add(self.onmag_si, self.offmag, self.guardar)
                        self.popup_mag.add_to_group()
                        self.parent.config.set_preference("magnificador", True)

                    elif sprite[0].id == "offmag":
                        self.button_group.remove(self.onmag_si, self.offmag)
                        self.button_group.add(self.onmag, self.offmag_si, self.guardar)
                        self.popup_mag.remove_from_group()
                        self.parent.config.set_preference("magnificador", False)

                    elif sprite[0].id == "oflector":
                        self.button_group.remove(
                            self.lector_si,
                            self.oflector,
                            self.vbaja,
                            self.vbaja_sel,
                            self.vmedia,
                            self.vmedia_sel,
                            self.vrapida,
                            self.vrapida_sel,
                            self.guardar,
                        )
                        self.word_group.remove(
                            self.q4_label.words, self.q4_options.words
                        )
                        # synvel rollback removed — set_preference writes to in-memory store directly.
                        self.button_group.add(
                            self.lector, self.oflector_si, self.guardar
                        )
                        self.parent.config.set_screen_reader_enabled(False)

                    elif sprite[0].id == "lector":
                        self.button_group.remove(
                            self.lector, self.oflector_si, self.guardar
                        )
                        if self.parent.config.get_preference("synvel", "baja") == "baja":
                            self.button_group.add(
                                self.lector_si,
                                self.oflector,
                                self.vbaja_sel,
                                self.vmedia,
                                self.vrapida,
                                self.guardar,
                            )
                        elif self.parent.config.get_preference("synvel", "baja") == "media":
                            self.button_group.add(
                                self.lector_si,
                                self.oflector,
                                self.vbaja,
                                self.vmedia_sel,
                                self.vrapida,
                                self.guardar,
                            )
                        elif self.parent.config.get_preference("synvel", "baja") == "rapida":
                            self.button_group.add(
                                self.lector_si,
                                self.oflector,
                                self.vbaja,
                                self.vmedia,
                                self.vrapida_sel,
                                self.guardar,
                            )
                        self.word_group.add(
                            self.q4_label.words, self.q4_options.words
                        )
                        self.parent.config.set_screen_reader_enabled(True)

                    elif sprite[0].id == "vbaja":
                        self.button_group.remove(
                            self.vbaja,
                            self.vmedia_sel,
                            self.vrapida,
                            self.vrapida_sel,
                            self.guardar,
                        )
                        self.button_group.add(
                            self.vbaja_sel, self.vmedia, self.vrapida, self.guardar
                        )
                        self.parent.config.set_preference("synvel", "baja")

                    elif sprite[0].id == "vmedia":
                        self.button_group.remove(
                            self.vbaja,
                            self.vbaja_sel,
                            self.vmedia,
                            self.vrapida,
                            self.vrapida_sel,
                            self.guardar,
                        )
                        self.button_group.add(
                            self.vbaja, self.vmedia_sel, self.vrapida, self.guardar
                        )
                        self.parent.config.set_preference("synvel", "media")

                    elif sprite[0].id == "vrapida":
                        self.button_group.remove(
                            self.vbaja,
                            self.vbaja_sel,
                            self.vmedia,
                            self.vmedia_sel,
                            self.vrapida,
                            self.guardar,
                        )
                        self.button_group.add(
                            self.vbaja, self.vmedia, self.vrapida_sel, self.guardar
                        )
                        self.parent.config.set_preference("synvel", "rapida")

                    elif sprite[0].id == "guardar":
                        self.speech_server.stopserver()
                        self.parent.config.set_preference("cache", True)
                        if (
                            self.parent.config.get_font_size()
                            != self.parent.config.get_preference("t_fuente", 18)
                        ):
                            self.parent.set_text_change_enabled(True)
                        self.parent.config.flush()
                        self.speech_server.update_server()
                        self.clear_groups()
                        if self.parent.first_run:
                            self.parent.changeState(pantalla2.Screen(self.parent))
                        else:
                            if self.is_overlay:
                                self.parent.RETURN_TO_PREV_SCREEN = True
                            self.parent.popState()

    def update(self):
        """Update cursor position, magnifier, and button tooltips."""
        self.mouse.update()
        self.magnifier.magnificar(self.parent.screen)
        self.button_group.update(self.tooltip_group)
