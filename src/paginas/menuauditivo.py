#!/usr/bin/env python

import pygame

from components import screen
from components.texto import Text

animations = [
    "colors-man",
    "colors-woman",
]

banners = [
    "banner-inf",
    "banner-acc-sordo",
]

buttons = [
    "velocidad",
    "si",
    "no",
    "check_si",
    "check_no",
    "gender-girl-btn",
    "gender-boy-btn",
    "gender-girl-sel-btn",
    "gender-boy-sel-btn",
    "puerta",
    "guardar",
    "hoja",
    "amarillo",
    "rosado",
    "rojo",
    "v_hombre",
    "v_mujer",
]


class Screen(screen.Screen):
    """Auditory accessibility configuration screen for selecting the virtual interpreter and avatar settings."""

    def __init__(self, parent, is_overlay=False):
        """
        Initialise the screen.

        @param parent: Screen manager instance.
        @type parent: Manejador
        @param is_overlay: True if this screen is pushed over another; False if loaded via changeState.
        @type is_overlay: bool
        """
        self.name = "screen_aud"
        super().__init__(parent, self.name)
        self.is_overlay = is_overlay
        self.speech_server.processtext(
            self.parent.text_loader.ui("config_screens", "auditory", "title_reader"),
            False,
        )
        self.load_buttons(buttons)
        self.female_shirts = [self.amarillo, self.rosado, self.v_mujer]
        self.male_shirts = [self.amarillo, self.rojo, self.v_hombre]
        self.q1_label        = self._label(310, 70,  "q1_interpreter")
        self.q1_options      = self._label(400, 120, "opt_yes_no",   right=800)
        self.q2_label        = self._label(310, 150, "q2_gender")
        self.q2_options      = self._label(400, 200, "opt_f_m",      right=800)
        self.q3_label_male   = self._label(310, 240, "q3_color_m")
        self.q3_label_female = self._label(310, 240, "q3_color_f")
        self.q4_label_male   = self._label(310, 330, "q4_speed_m",   right=800)
        self.q4_label_female = self._label(310, 330, "q4_speed_f",   right=800)
        self.save_hint_label = self._label(200, 400, "save_hint",    right=800)

        self.load_animations(animations)
        self.load_banners(banners)
        self._load_preferences()
        self.button_actions = {
            "velocidad":       self._go_velocidad,
            "puerta":          lambda: (self.clear_groups(), self.parent.popState()),
            "si":              self._go_si,
            "no":              self._go_no,
            "gender-boy-btn":  self._go_gender_boy,
            "gender-girl-btn": self._go_gender_girl,
            "amarillo":        self._go_amarillo,
            "rojo":            lambda: self._select_color(self.colors_man,   self.q4_label_male,   1),
            "rosado":          lambda: self._select_color(self.colors_woman, self.q4_label_female, 1),
            "v_hombre":        lambda: self._select_color(self.colors_man,   self.q4_label_male,   2),
            "v_mujer":         lambda: self._select_color(self.colors_woman, self.q4_label_female, 2),
            "guardar":         self._go_guardar,
        }

    def _label(self, x, y, key, right=700):
        """Create a config-screen Text label with standard size=20, text_type=1."""
        return Text(x, y, self.parent.text_loader.ui("config_screens", "auditory", key), 20, 1, right)

    def _load_preferences(self):
        """Populate sprite groups from saved preferences, or fall back to defaults if no configuration exists."""
        self.word_group.add(self.q1_label.words, self.q1_options.words)
        self.banner_group.add(self.banner_acc_sordo, self.banner_inf)
        if self.parent.config.get_preference("cache", False) == True:
            if self.parent.config.get_preference("disc_audi", False) == True:
                self.button_group.add(
                    self.no,
                    self.check_si,
                    self.puerta,
                    self.guardar,
                    self.velocidad,
                    self.hoja,
                )
                if self.parent.config.get_preference("genero", "") == "Mujer":
                    self.anim_group.add(self.colors_woman)
                    self.colors_woman.set_frame(self.parent.config.get_preference("color", 0))
                    self.button_group.add(
                        self.gender_boy_btn,
                        self.gender_girl_sel_btn,
                        self.amarillo,
                        self.rosado,
                        self.v_mujer,
                    )
                    self.word_group.add(
                        self.q2_label.words,
                        self.q2_options.words,
                        self.q3_label_female.words,
                        self.q4_label_female.words,
                        self.save_hint_label.words,
                    )
                elif self.parent.config.get_preference("genero", "") == "Hombre":
                    self.anim_group.add(self.colors_man)
                    self.colors_man.set_frame(self.parent.config.get_preference("color", 0))
                    self.button_group.add(
                        self.gender_girl_btn,
                        self.gender_boy_sel_btn,
                        self.amarillo,
                        self.rojo,
                        self.v_hombre,
                    )
                    self.word_group.add(
                        self.q2_label.words,
                        self.q2_options.words,
                        self.q3_label_male.words,
                        self.q4_label_male.words,
                        self.save_hint_label.words,
                    )
                self.colors_man.set_speed(self.parent.config.get_animation_speed())
                self.colors_woman.set_speed(self.parent.config.get_animation_speed())
                self.hoja.relocate(x=self.parent.config.get_preference("ubx", 499))
            elif self.parent.config.get_preference("disc_audi", False) == False:
                self.word_group.add(self.save_hint_label.words)
                self.button_group.add(
                    self.si, self.check_no, self.puerta, self.guardar
                )
        else:
            self.button_group.add(self.si, self.check_no, self.puerta)
            self.hoja.relocate(x=499)
            self.colors_man.set_speed(self.parent.config.get_animation_speed())
            self.colors_woman.set_speed(self.parent.config.get_animation_speed())
            self.colors_man.set_frame(self.parent.config.get_preference("color", 0))
            self.colors_woman.set_frame(self.parent.config.get_preference("color", 0))

    def _save_and_exit(self):
        """Persist the current preferences and return to the previous or main screen."""
        self.parent.config.set_preference("cache", True)
        if (
            self.parent.config.get_font_size()
            != self.parent.config.get_preference("t_fuente", 18)
        ):
            self.parent.config.set_text_change_enabled(True)
        self.parent.config.flush()
        self.parent.finish_config(self)

    def _select_color(self, anim, label, frame):
        """Swap in anim at frame and show label; always clears both q4 labels first (idempotent)."""
        self.anim_group.empty()
        self.word_group.remove(self.q4_label_female.words, self.q4_label_male.words)
        self.button_group.add(self.velocidad, self.hoja)
        self.anim_group.add(anim)
        self.word_group.add(label.words)
        anim.set_frame(frame)
        self.parent.config.set_preference("color", anim.frame_row)
        anim.continuar()

    def _go_velocidad(self):
        (x, _) = pygame.mouse.get_pos()
        (posx, _, width, _) = self.velocidad.rect
        (_, _, radio, _) = self.hoja.rect
        if x > posx + (radio / 2) and x < posx + width - radio / 2:
            factor = (x - posx) / float(width - radio)
            factor_anim = (posx + width - x) / 8
            ux = x - radio / 2
            self.hoja.relocate(x=ux)
            if factor_anim < 2:
                factor_anim = 2
            if factor > 1:
                factor = 1
            self.colors_woman.set_speed(int(factor_anim))
            self.colors_man.set_speed(int(factor_anim))
            self.parent.config.set_preference("vel_anim", factor_anim)
            self.parent.config.set_preference("velocidad", factor)
            self.parent.config.set_preference("ubx", ux)

    def _go_si(self):
        self.button_group.remove(self.check_no, self.si, self.guardar)
        self.word_group.remove(self.save_hint_label.words)
        self.button_group.add(
            self.gender_boy_btn, self.gender_girl_btn, self.check_si, self.no
        )
        self.word_group.add(self.q2_label.words, self.q2_options.words)
        self.parent.config.set_preference("disc_audi", True)

    def _go_no(self):
        self.anim_group.empty()
        self.button_group.remove(
            self.velocidad,
            self.hoja,
            self.check_si,
            self.no,
            self.gender_boy_btn,
            self.gender_girl_btn,
            self.gender_girl_sel_btn,
            self.gender_boy_sel_btn,
            self.male_shirts,
            self.female_shirts,
        )
        self.button_group.add(self.check_no, self.si, self.guardar)
        self.word_group.add(self.save_hint_label.words)
        self.word_group.remove(
            self.q2_label.words,
            self.q2_options.words,
            self.q3_label_female.words,
            self.q4_label_female.words,
            self.q3_label_male.words,
            self.q4_label_male.words,
        )
        self.parent.config.set_preference("disc_audi", False)

    def _go_gender_boy(self):
        self.anim_group.empty()
        self.word_group.remove(
            self.q3_label_female.words,
            self.q4_label_female.words,
            self.q4_label_male.words,
        )
        self.anim_group.add(self.colors_man)
        self.colors_man.detener()
        self.word_group.add(self.q3_label_male.words, self.save_hint_label.words)
        self.button_group.remove(
            self.velocidad,
            self.hoja,
            self.female_shirts,
            self.gender_boy_btn,
            self.gender_girl_sel_btn,
        )
        self.button_group.add(
            self.gender_boy_sel_btn,
            self.gender_girl_btn,
            self.guardar,
            self.male_shirts,
        )
        self.parent.config.set_preference("genero", "Hombre")

    def _go_gender_girl(self):
        self.anim_group.empty()
        self.word_group.remove(
            self.q3_label_male.words,
            self.q4_label_male.words,
        )
        self.anim_group.add(self.colors_woman)
        self.colors_woman.detener()
        self.word_group.add(self.q3_label_female.words, self.save_hint_label.words)
        self.button_group.remove(
            self.velocidad,
            self.hoja,
            self.male_shirts,
            self.gender_girl_btn,
            self.gender_boy_sel_btn,
        )
        self.button_group.add(
            self.gender_girl_sel_btn,
            self.gender_boy_btn,
            self.guardar,
            self.female_shirts,
        )
        self.parent.config.set_preference("genero", "Mujer")

    def _go_amarillo(self):
        if self.parent.config.get_preference("genero", "") == "Mujer":
            self._select_color(self.colors_woman, self.q4_label_female, 0)
        else:
            self._select_color(self.colors_man, self.q4_label_male, 0)

    def _go_guardar(self):
        if (
            self.parent.config.get_preference("velocidad", 0.5) == 0.5
            and self.parent.config.get_animation_speed() == 4
        ):
            self.parent.config.set_preference("ubx", self.hoja.x)
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
            elif pygame.sprite.spritecollideany(self.mouse, self.button_group):
                sprite = pygame.sprite.spritecollide(self.mouse, self.button_group, False)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.button_actions.get(sprite[0].id, lambda: None)()
        self.handle_magnifier(events)

