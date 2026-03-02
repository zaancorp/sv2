#!/usr/bin/env python

import pygame

from components import screen
from components.texto import Text
from paginas import pantalla2

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
        self.parent = parent
        super().__init__(parent, self.name)
        self.is_overlay = is_overlay
        self.speech_server.processtext(
            self.parent.text_loader.ui("config_screens", "auditory", "title_reader"),
            False,
        )
        self.load_buttons(buttons)
        self.female_shirts = [self.amarillo, self.rosado, self.v_mujer]
        self.male_shirts = [self.amarillo, self.rojo, self.v_hombre]
        self.q1_label = Text(
            310,
            70,
            self.parent.text_loader.ui("config_screens", "auditory", "q1_interpreter"),
            20,
            1,
            700,
        )
        self.q1_options = Text(
            400,
            120,
            self.parent.text_loader.ui("config_screens", "auditory", "opt_yes_no"),
            20,
            1,
            800,
        )
        self.q2_label = Text(
            310,
            150,
            self.parent.text_loader.ui("config_screens", "auditory", "q2_gender"),
            20,
            1,
            700,
        )
        self.q2_options = Text(
            400,
            200,
            self.parent.text_loader.ui("config_screens", "auditory", "opt_f_m"),
            20,
            1,
            800,
        )
        self.q3_label_male = Text(
            310,
            240,
            self.parent.text_loader.ui("config_screens", "auditory", "q3_color_m"),
            20,
            1,
            700,
        )
        self.q3_label_female = Text(
            310,
            240,
            self.parent.text_loader.ui("config_screens", "auditory", "q3_color_f"),
            20,
            1,
            700,
        )
        self.q4_label_male = Text(
            310,
            330,
            self.parent.text_loader.ui("config_screens", "auditory", "q4_speed_m"),
            20,
            1,
            800,
        )
        self.q4_label_female = Text(
            310,
            330,
            self.parent.text_loader.ui("config_screens", "auditory", "q4_speed_f"),
            20,
            1,
            800,
        )
        self.save_hint_label = Text(
            200,
            400,
            self.parent.text_loader.ui("config_screens", "auditory", "save_hint"),
            20,
            1,
            800,
        )

        self.load_animations(animations)
        self.load_banners(banners)
        self.load_preferences()

    def load_preferences(self):
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

    def handleEvents(self, events):
        """
        Process input events for this screen.

        @param events: Event list from the main loop.
        @type events: list
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.parent.quit()

            if pygame.sprite.spritecollideany(self.mouse, self.button_group):
                sprite = pygame.sprite.spritecollide(
                    self.mouse, self.button_group, False
                )
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if sprite[0].id == "velocidad":
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

                    elif sprite[0].id == "puerta":
                        self.clear_groups()
                        self.parent.popState()

                    elif sprite[0].id == "si":
                        self.button_group.remove(self.check_no, self.si, self.guardar)
                        self.word_group.remove(self.save_hint_label.words)
                        self.button_group.add(
                            self.gender_boy_btn, self.gender_girl_btn, self.check_si, self.no
                        )
                        self.word_group.add(
                            self.q2_label.words, self.q2_options.words
                        )
                        self.parent.config.set_preference("disc_audi", True)

                    elif sprite[0].id == "no":
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

                    elif sprite[0].id == "gender-boy-btn":
                        self.anim_group.empty()
                        self.word_group.remove(
                            self.q3_label_female.words,
                            self.q3_label_female.words,
                            self.q4_label_female.words,
                            self.q3_label_female.words,
                        )
                        self.anim_group.add(self.colors_man)
                        self.colors_man.detener()
                        self.word_group.add(
                            self.q3_label_male.words, self.save_hint_label.words
                        )
                        self.word_group.remove(self.q4_label_male.words)
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

                    elif sprite[0].id == "gender-girl-btn":
                        self.anim_group.empty()
                        self.word_group.remove(
                            self.q3_label_male.words,
                            self.q3_label_male.words,
                            self.q4_label_male.words,
                            self.q3_label_male.words,
                        )
                        self.anim_group.add(self.colors_woman)
                        self.colors_woman.detener()
                        self.word_group.add(
                            self.q3_label_female.words, self.save_hint_label.words
                        )
                        self.word_group.remove(self.q4_label_male.words)
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

                    elif sprite[0].id == "amarillo":
                        self.anim_group.empty()
                        self.button_group.add(self.velocidad, self.hoja)
                        self.word_group.remove(
                            self.q4_label_female.words, self.q4_label_male.words
                        )
                        if self.parent.config.get_preference("genero", "") == "Mujer":
                            self.word_group.add(self.q4_label_female.words)
                            self.anim_group.add(self.colors_woman)
                            self.colors_woman.set_frame(0)
                            self.parent.config.set_preference("color", self.colors_woman.frame_row)
                            self.colors_woman.continuar()
                        else:
                            self.word_group.add(self.q4_label_male.words)
                            self.anim_group.add(self.colors_man)
                            self.colors_man.set_frame(0)
                            self.parent.config.set_preference("color", self.colors_man.frame_row)
                            self.colors_man.continuar()

                    elif sprite[0].id == "rojo":
                        self.anim_group.empty()
                        self.word_group.remove(self.q4_label_female.words)
                        self.button_group.add(self.velocidad, self.hoja)
                        self.anim_group.add(self.colors_man)
                        self.word_group.add(self.q4_label_male.words)
                        self.colors_man.set_frame(1)
                        self.parent.config.set_preference("color", self.colors_man.frame_row)
                        self.colors_man.continuar()

                    elif sprite[0].id == "rosado":
                        self.anim_group.empty()
                        self.word_group.remove(self.q4_label_male.words)
                        self.button_group.add(self.velocidad, self.hoja)
                        self.anim_group.add(self.colors_woman)
                        self.word_group.add(self.q4_label_female.words)
                        self.colors_woman.set_frame(1)
                        self.parent.config.set_preference("color", self.colors_woman.frame_row)
                        self.colors_woman.continuar()

                    elif sprite[0].id == "v_hombre":
                        self.anim_group.empty()
                        self.word_group.remove(self.q4_label_female.words)
                        self.button_group.add(self.velocidad, self.hoja)
                        self.anim_group.add(self.colors_man)
                        self.word_group.add(self.q4_label_male.words)
                        self.colors_man.set_frame(2)
                        self.parent.config.set_preference("color", self.colors_man.frame_row)
                        self.colors_man.continuar()

                    elif sprite[0].id == "v_mujer":
                        self.anim_group.empty()
                        self.word_group.remove(self.q4_label_female.words)
                        self.button_group.add(self.velocidad, self.hoja)
                        self.anim_group.add(self.colors_woman)
                        self.word_group.add(self.q4_label_female.words)
                        self.colors_woman.set_frame(2)
                        self.parent.config.set_preference("color", self.colors_woman.frame_row)
                        self.colors_woman.continuar()

                    elif sprite[0].id == "guardar":
                        if (
                            self.parent.config.get_preference("velocidad", 0.5) == 0.5
                            and self.parent.config.get_animation_speed() == 4
                        ):
                            self.parent.config.set_preference("ubx", self.hoja.x)
                        self.parent.config.set_preference("cache", True)
                        if (
                            self.parent.config.get_font_size()
                            != self.parent.config.get_preference("t_fuente", 18)
                        ):
                            self.parent.set_text_change_enabled(True)
                        self.parent.config.flush()
                        self.clear_groups()
                        if self.parent.first_run:
                            self.parent.changeState(pantalla2.Screen(self.parent))
                        else:
                            if self.is_overlay:
                                self.parent.RETURN_TO_PREV_SCREEN = True
                            self.parent.popState()
        self.handle_magnifier(events)

    def update(self):
        """Update cursor position, magnifier, and button tooltips."""
        self.mouse.update()
        self.magnifier.magnificar(self.parent.screen)
        self.button_group.update(self.tooltip_group)
