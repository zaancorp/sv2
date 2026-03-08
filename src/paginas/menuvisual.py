#!/usr/bin/env python

import pygame

from components import screen
from components.texto import Text
from components.popups import PopUp

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
        self.q1_label        = self._label(10,  70,  "q1_magnifier")
        self.q1_options      = self._label(100, 120, "opt_yes_no",        right=500)
        self.q3_label        = self._label(10,  250, "q3_screen_reader")
        self.q3_options      = self._label(100, 300, "opt_yes_no",        right=500)
        self.q4_label        = self._label(10,  340, "q4_reader_speed")
        self.q4_options      = self._label(40,  390, "opt_reader_speeds",  right=500)
        self.save_hint_label = self._label(200, 400, "save_hint",          right=500)
        self.q2_label        = self._label(10,  160, "q2_font_size")
        self.q2_options      = self._label(100, 200, "opt_font_sizes")
        instrucciones = self.parent.text_loader.ui(
            "config_screens", "visual", "reader_instructions"
        )
        self.reader_prompt1 = self.parent.text_loader.ui("config_screens", "visual", "reader_q1")
        self.reader_prompt2 = self.parent.text_loader.ui("config_screens", "visual", "reader_q2")

        self.load_banners(banners)
        self.load_buttons(buttons)
        self._load_preferences()
        self.speech_server.stopserver()
        self.opcion = 1
        self.speech_server.processtext(instrucciones + self.reader_prompt1, True)
        self.button_actions = {
            "puerta":   lambda: (self.clear_groups(), self.parent.popState()),
            "tam18":    lambda: self._select_font_size(18),
            "tam20":    lambda: self._select_font_size(20),
            "tam22":    lambda: self._select_font_size(22),
            "onmag":    lambda: self._set_magnifier(True),
            "offmag":   lambda: self._set_magnifier(False),
            "lector":   self._enable_reader,
            "oflector": self._disable_reader,
            "vbaja":    lambda: self._select_synvel("baja"),
            "vmedia":   lambda: self._select_synvel("media"),
            "vrapida":  lambda: self._select_synvel("rapida"),
            "guardar":  self._save_and_exit,
        }

    def _label(self, x, y, key, right=400):
        """Create a config-screen Text label with standard size=20, text_type=1."""
        return Text(x, y, self.parent.text_loader.ui("config_screens", "visual", key), 20, 1, right)

    def _load_preferences(self):
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

    def _save_and_exit(self):
        """Persist the current preferences and return to the previous or main screen."""
        self.speech_server.stopserver()
        self.parent.config.set_preference("cache", True)
        if (
            self.parent.config.get_font_size()
            != self.parent.config.get_preference("t_fuente", 18)
        ):
            self.parent.config.set_text_change_enabled(True)
        self.parent.config.flush()
        self.speech_server.update_server()
        self.parent.finish_config(self)

    def _select_font_size(self, size):
        """Select font size; swaps all six tam buttons and shows the save button."""
        size_map = {
            18: (self.tam18_sel, self.tam20,     self.tam22),
            20: (self.tam18,     self.tam20_sel, self.tam22),
            22: (self.tam18,     self.tam20,     self.tam22_sel),
        }
        self.button_group.remove(
            self.tam18, self.tam18_sel,
            self.tam20, self.tam20_sel,
            self.tam22, self.tam22_sel,
            self.guardar,
        )
        self.button_group.add(*size_map[size], self.guardar)
        self.parent.config.set_preference("t_fuente", size)

    def _set_magnifier(self, enabled):
        """Toggle the magnifier on or off and update button state."""
        if enabled:
            self.button_group.remove(self.onmag, self.offmag_si)
            self.button_group.add(self.onmag_si, self.offmag, self.guardar)
            self.popup_mag.add_to_group()
        else:
            self.button_group.remove(self.onmag_si, self.offmag)
            self.button_group.add(self.onmag, self.offmag_si, self.guardar)
            self.popup_mag.remove_from_group()
        self.parent.config.set_preference("magnificador", enabled)

    def _enable_reader(self):
        """Enable the screen reader and show the speed selector for the saved synvel preference."""
        self.button_group.remove(self.lector, self.oflector_si, self.guardar)
        speed_map = {
            "baja":   (self.vbaja_sel, self.vmedia,     self.vrapida),
            "media":  (self.vbaja,     self.vmedia_sel,  self.vrapida),
            "rapida": (self.vbaja,     self.vmedia,      self.vrapida_sel),
        }
        synvel = self.parent.config.get_preference("synvel", "baja")
        self.button_group.add(
            self.lector_si, self.oflector, *speed_map[synvel], self.guardar
        )
        self.word_group.add(self.q4_label.words, self.q4_options.words)
        self.parent.config.set_screen_reader_enabled(True)

    def _disable_reader(self):
        """Disable the screen reader and remove the speed selector."""
        self.button_group.remove(
            self.lector_si, self.oflector,
            self.vbaja, self.vbaja_sel,
            self.vmedia, self.vmedia_sel,
            self.vrapida, self.vrapida_sel,
            self.guardar,
        )
        self.word_group.remove(self.q4_label.words, self.q4_options.words)
        self.button_group.add(self.lector, self.oflector_si, self.guardar)
        self.parent.config.set_screen_reader_enabled(False)

    def _select_synvel(self, speed):
        """Select the TTS speed; swaps all six speed buttons and shows the save button."""
        speed_map = {
            "baja":   (self.vbaja_sel, self.vmedia,     self.vrapida),
            "media":  (self.vbaja,     self.vmedia_sel,  self.vrapida),
            "rapida": (self.vbaja,     self.vmedia,      self.vrapida_sel),
        }
        self.button_group.remove(
            self.vbaja, self.vbaja_sel,
            self.vmedia, self.vmedia_sel,
            self.vrapida, self.vrapida_sel,
            self.guardar,
        )
        self.button_group.add(*speed_map[speed], self.guardar)
        self.parent.config.set_preference("synvel", speed)

    def handle_key_input(self, key):
        """
        Advance the screen-reader configuration wizard based on the key pressed.

        @param key: Numeric key code representing the user's selection (1, 2, 3, or 4 for confirm).
        @type key: int
        """
        if self.opcion == 1:
            if key == 1:
                self.speech_server.stopserver()
                self._enable_reader()
                self.speech_server.processtext(self.reader_prompt2, True)
                self.opcion += 1
            elif key == 2:
                self.opcion = 3
                self._disable_reader()
                self.speech_server.processtext(
                    self.parent.text_loader.ui("config_screens", "visual", "reader_success"),
                    True,
                )
        elif self.opcion == 2:
            speeds = {1: "baja", 2: "media", 3: "rapida"}
            if key in speeds:
                self._select_synvel(speeds[key])
                self.opcion += 1
                self.speech_server.processtext(
                    self.parent.text_loader.ui("config_screens", "visual", "reader_success"),
                    True,
                )
        elif self.opcion == 3:
            if key == 4:
                self._save_and_exit()

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
                if event.key == pygame.K_ESCAPE:
                    self.clear_groups()
                    if self.is_overlay:
                        self.parent.RETURN_TO_PREV_SCREEN = True
                    self.parent.popState()
                else:
                    key_map = {
                        pygame.K_1: 1, pygame.K_2: 2,
                        pygame.K_3: 3, pygame.K_RETURN: 4,
                    }
                    if event.key in key_map:
                        self.handle_key_input(key_map[event.key])
            elif pygame.sprite.spritecollideany(self.mouse, self.button_group):
                sprite = pygame.sprite.spritecollide(self.mouse, self.button_group, False)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.button_actions.get(sprite[0].id, lambda: None)()

