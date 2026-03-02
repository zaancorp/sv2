#!/usr/bin/env python

import random
import pygame

from components import screen
from components.popups import PopUp
from components.cursor import Cursor
from components.image import Image
from components.object import PropObject
from components.boundary import Boundary
from components.marker import Marker
from components.button import Button, RenderButton
from components.character import Character, RenderChar
from components.animations import Animation, RenderAnim


class Screen(screen.Screen):
    """Two-level farming activity screen where the player collects objects and answers vocabulary questions."""

    elapsed_ms = 0
    clock = pygame.time.Clock()
    anim_fondo = RenderAnim()
    button_group = RenderButton()
    character_group = RenderChar()
    sprite = pygame.sprite.Sprite()
    current_marker = pygame.sprite.Sprite()
    boundaries = pygame.sprite.Group()
    prop_group = pygame.sprite.Group()
    marker_group = pygame.sprite.Group()
    popup_group = pygame.sprite.OrderedUpdates()
    prop_image_group = pygame.sprite.OrderedUpdates()
    narration_pending = True
    hint_active = False
    prop_collision = False
    marker = False
    completed = False
    timer_done = True
    timer_started = False
    text_visible = False
    announce_position = False
    tts_silent = True
    sound_tutorial_active = False
    level = 1
    answer = 2
    cloud_speed = -2
    current_level = 1

    def __init__(self, parent):
        """
        Initialise the activity: load all assets, build popup objects, and queue level 1.

        @param parent: Screen manager instance.
        @type parent: Manejador
        """
        self.img_clapping = pygame.image.load(self.popups_path + "aplaudiendo.png").convert_alpha()
        self.img_thinking = pygame.image.load(self.popups_path + "pensando.png").convert_alpha()
        poporquidea = pygame.image.load(self.popups_path + "orquidea.png").convert_alpha()
        popapamate = pygame.image.load(self.popups_path + "popupapamate.png").convert_alpha()
        poparaguaney = pygame.image.load(
            self.popups_path + "popuparaguaney.png"
        ).convert_alpha()
        popclorofila = pygame.image.load(
            self.popups_path + "popupclorofila.png"
        ).convert_alpha()
        popinjerto = pygame.image.load(self.popups_path + "popupinjerto.png").convert_alpha()
        poprepro = pygame.image.load(
            self.popups_path + "popupreproduccion.png"
        ).convert_alpha()
        popportu = pygame.image.load(self.popups_path + "portu.png").convert_alpha()
        popacodo = pygame.image.load(self.popups_path + "popuacodo.png").convert_alpha()
        popmango = pygame.image.load(self.popups_path + "popumango.png").convert_alpha()
        popyuca = pygame.image.load(self.popups_path + "popuyuca.png").convert_alpha()
        self.hint_images = {
            0: poparaguaney,
            1: popapamate,
            2: popclorofila,
            3: poporquidea,
            4: poprepro,
            5: popyuca,
            6: popmango,
            7: popportu,
            8: popacodo,
            9: popinjerto,
        }
        esc = pygame.image.load(self.popups_path + "esc.png").convert_alpha()
        mouse = pygame.image.load(self.popups_path + "touch.png").convert_alpha()
        active = pygame.image.load(self.popups_path + "boton-active.png").convert_alpha()
        enter = pygame.image.load(self.popups_path + "enter.png").convert_alpha()
        keyboard_active = pygame.image.load(self.popups_path + "flechas.png").convert_alpha()
        f1 = pygame.image.load(self.popups_path + "f1.png").convert_alpha()
        self.img_textos = {
            "ENTER": enter,
            "TECLADO": keyboard_active,
            "F1": f1,
            "ESC": esc,
            "SALIR": active,
            "RATON": mouse,
        }
        self.mouse = Cursor()
        self.parent = parent
        self.canvas = self.parent.screen
        pygame.display.set_caption("Siembra la semilla")
        # Text content for actividad 1 is loaded from JSON via TextLoader.
        self.activity1_data = self.parent.text_loader.require("activity1")
        self.activity1_questions = self.activity1_data["questions"]
        self.reset_questions()
        self.arrow_img = pygame.image.load(
            self.misc_path + "flecha-verde.png"
        ).convert_alpha()
        self.house = Image(0, 70, self.misc_path + "casa.png")
        self.pole = Image(880, 0, self.misc_path + "poste.png")
        self.tractor = Image(840, 80, self.misc_path + "tractor.png")
        self.shovel = PropObject(590, 380, self.misc_path + "pala.png", "la pala. ")
        self.fertilizer = PropObject(900, 305, self.misc_path + "abono.png", "el abono. ")
        self.cart = PropObject(200, 80, self.misc_path + "carre.png", "la carretilla. ")
        self.insec = PropObject(
            760, 140, self.misc_path + "insec.png", "el controlador biológico. "
        )
        self.watering_can = PropObject(
            792, 270, self.misc_path + "regadera.png", "la regadera. "
        )
        self.seeds = PropObject(
            450, 200, self.misc_path + "semillas.png", "las semillas. "
        )
        self.clouds = Animation(
            "nubes", self.misc_path + "nubes.png", 1, 1, 30, -15, -1, False, 18
        )
        self.exit_btn = Button(
            830, 60, "exit", "Salir", self.botones + "boton-active.png", 1, -1, False, 1
        )
        self.arrow_anim = Animation(
            "flecha", self.misc_path + "flecha-verde.png", 3, 1, 800, 350, -1, True, 6
        )
        self.flowers = Animation(
            "flores", self.misc_path + "campo-flores.png", 4, 1, 758, 290, -1, False, 18
        )
        self.planting_anim = Animation(
            "siembra", self.misc_path + "cinta-campesino.png", 3, 1, 680, 250, -1, True, 9
        )
        self.farmer = Character(200, 128, self.misc_path + "0.png", 2)
        self.popup_respuesta = PopUp(
            parent, ("Respuesta "), "Aceptar", self.arrow_img, self.popup_group
        )
        self.popup_pregunta = PopUp(
            parent,
            ("Pregunta ", "p1 ", "p2 ", "p3 "),
            "Aceptar",
            0,
            self.popup_group,
            1,
        )
        self.popup_help = PopUp(
            parent,
            self.activity1_data["instructions"]["popup"],
            "",
            self.img_textos,
            self.popup_group,
            2,
            512,
            214,
            100,
        )
        self.popup_instructions = PopUp(
            parent,
            "    Pulsa la tecla F1 para activar o desactivar las instrucciones del juego. ",
            "",
            self.img_textos,
            self.popup_group,
            2,
            240,
            482,
            -160,
        )
        self.popup_final1 = PopUp(
            self.parent,
            ("    ¡Muy bien! Has finalizado el primer nivel. ",),
            "Aceptar",
            self.img_clapping,
            self.popup_group,
        )
        self.update()

    def reset_questions(self):
        """Reset the available question pool and clear the current question selection."""
        self.remaining_question_ids = list(self.activity1_questions.keys())
        self.current_question_id = None

    def clear_groups(self):
        """Empty all sprite groups used by this activity."""
        self.character_group.empty()
        self.prop_image_group.empty()
        self.prop_group.empty()
        self.character_group.empty()
        self.button_group.empty()
        self.anim_fondo.empty()
        self.popup_group.empty()

    def start_level1(self):
        """Load assets and initialise all game objects for level 1 of activity 1."""
        self.reset_questions()
        self.current_level = 1
        self.completed = False
        self.narration_pending = True
        self.hint_active = False
        self.background = pygame.image.load(self.misc_path + "fondo1.png").convert()
        self.clear_groups()
        self.anim_fondo.empty()
        self.pole.relocate(880, 0)
        self.tractor.relocate(840, 80)
        self.seeds.relocate(450, 200)
        self.watering_can.relocate(880, 270)
        self.meta = pygame.Rect(800, 470, 50, 100)
        self.marker_group.empty()
        self.marker_seed = Marker((357, 314, 20, 20), "semilla")
        self.seed_collect_marker = Marker((357, 234, 20, 20), "semilla1")
        self.marker_can = Marker((664, 314, 20, 20), "regadera")
        self.can_collect_marker = Marker((786, 314, 20, 20), "regadera1")
        self.marker_shovel = Marker((501, 314, 20, 20), "pala")
        self.marker_group.add(self.marker_seed, self.marker_can)
        self.boundaries.empty()
        self.boundaries.add(
            Boundary((167, 267, 170, 20), 1),
            Boundary((317, 196, 20, 91), 2),
            Boundary((317, 196, 113, 20), 3),
            Boundary((410, 196, 20, 91), 4),
            Boundary((410, 267, 430, 20), 5),
            Boundary((167, 267, 20, 117), 6),
            Boundary((820, 267, 20, 117), 7),
            Boundary((167, 364, 310, 20), 8),
            Boundary((550, 364, 290, 20), 9),
            Boundary((457, 364, 20, 208), 10),
            Boundary((550, 364, 20, 122), 11),
            Boundary((550, 466, 169, 20), 12),
            Boundary((699, 466, 20, 106), 13),
            Boundary((457, 552, 262, 20), 14),
        )
        self.farmer.reset(170, 128, self.misc_path + "0.png", 2, self.boundaries)
        self.character_group.add(self.farmer)
        self.farmer.update_rects()
        self.prop_group.add(self.seeds, self.watering_can, self.shovel)
        self.prop_image_group.add(self.tractor, self.pole, self.house)
        self.button_group.add(self.exit_btn)
        self.anim_fondo.add(self.clouds, self.flowers)
        self.popup_instructions.add_to_group()
        self.flowers.detener()
        self.show_help_popup()
        if self.parent.config.is_screen_reader_enabled():
            self.boundaries.add(Boundary((477, 365, 73, 20), 15))

    def start_level2(self):
        """Load assets and initialise all game objects for level 2 of activity 1."""
        self.current_level = 2
        self.completed = False
        self.narration_pending = True
        self.hint_active = False
        self.background = pygame.image.load(self.misc_path + "fondo2.png").convert()
        self.clear_groups()
        self.pole.relocate(880, -70)
        self.tractor.relocate(840, 20)
        self.seeds.relocate(290, 300)
        self.watering_can.relocate(495, 125)
        self.meta = pygame.Rect(800, 400, 50, 80)
        self.marker_group.empty()
        self.marker_seed_cart = Marker((206, 246, 20, 20), "sem_car")
        self.marker_can = Marker((424, 246, 20, 20), "regadera")
        self.marker_shovel = Marker((510, 246, 20, 20), "pala")
        self.marker_insect = Marker((645, 246, 20, 20), "insec")
        self.marker_fertilizer = Marker((808, 246, 20, 20), "abono")
        self.seed_collect_marker = Marker((206, 315, 20, 20), "semillas1")
        self.can_collect_marker = Marker((424, 180, 20, 20), "regadera1")
        self.cart_collect_marker = Marker((206, 180, 20, 20), "carretilla1")
        self.insect_collect_marker = Marker((645, 180, 20, 20), "insect1")
        self.fertilizer_collect_marker = Marker((808, 315, 20, 20), "abono1")
        self.boundaries.empty()
        self.boundaries.add(
            Boundary((153, 124, 20, 259), 1),
            Boundary((153, 124, 113, 20), 2),
            Boundary((246, 124, 20, 92), 3),
            Boundary((246, 196, 151, 20), 4),
            Boundary((377, 124, 20, 92), 5),
            Boundary((377, 124, 113, 20), 6),
            Boundary((470, 124, 20, 92), 7),
            Boundary((470, 196, 148, 20), 8),
            Boundary((598, 124, 20, 92), 9),
            Boundary((598, 124, 117, 20), 10),
            Boundary((695, 124, 20, 92), 11),
            Boundary((695, 196, 177, 20), 12),
            Boundary((852, 196, 20, 187), 13),
            Boundary((760, 363, 112, 20), 13),
            Boundary((760, 293, 20, 90), 14),
            Boundary((555, 293, 225, 20), 15),
            Boundary((555, 293, 20, 120), 16),
            Boundary((555, 393, 170, 20), 17),
            Boundary((705, 393, 20, 118), 18),
            Boundary((463, 491, 262, 20), 19),
            Boundary((463, 293, 20, 218), 20),
            Boundary((246, 293, 237, 20), 21),
            Boundary((246, 293, 20, 90), 22),
            Boundary((153, 363, 113, 20), 23),
        )
        self.farmer.reset(150, 50, self.misc_path + "-1.png", 2, self.boundaries)
        self.farmer.update_rects()
        self.farmer.marker_code = -1
        self.character_group.add(self.farmer)
        self.prop_group.add(
            self.cart, self.shovel, self.watering_can, self.seeds, self.fertilizer, self.insec
        )
        self.prop_image_group.add(self.tractor, self.pole)
        self.anim_fondo.add(self.clouds, self.flowers)
        self.popup_instructions.add_to_group()
        self.button_group.add(self.exit_btn)
        self.flowers.detener()
        if self.parent.config.is_screen_reader_enabled():
            self.boundaries.add(Boundary((483, 294, 72, 20), 24))  # Ladrillo invisible
            self.start_sound_tutorial()

    def show_help_popup(self):
        """Toggle the instructions popup and update TTS accordingly."""
        if self.hint_active == False:
            self.popup_help.add_to_group()
            self.speech_server.processtext(
                self.activity1_data["instructions"]["reader"],
                self.parent.config.is_screen_reader_enabled(),
            )
            self.hint_active = True
        else:
            self.popup_help.remove_from_group()
            self.speech_server.stopserver()
            self.hint_active = False
            if self.popup_pregunta.activo:
                self.speak_answers(
                    self.activity1_questions[self.current_question_id]["prompt"],
                    self.activity1_questions[self.current_question_id]["options"],
                    True,
                )
            elif self.popup_respuesta.activo:
                self.speech_server.processtext(
                    self.activity1_questions[self.current_question_id]["hints"][
                        self.cache_click
                    ]
                    + "Pulsa Enter para continuar. ",
                    self.parent.config.is_screen_reader_enabled(),
                )

    def start_sound_tutorial(self):
        """Start the timer used to synchronise TTS narration with instructional sound cues."""
        self.timer_clock = pygame.time.Clock()
        self.timer_clock.tick(30)
        self.timer_started = True
        self.timer_done = False

    def handleEvents(self, events):
        """
        Process input events for this screen.

        @param events: Event list from the main loop.
        @type events: list
        """
        self.teclasPulsadas = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.parent.popState()

            if event.type == pygame.QUIT:
                self.parent.quit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                if not self.completed:
                    self.show_help_popup()

                if not self.sound_tutorial_active and self.parent.config.is_screen_reader_enabled():
                    self.popup_help.remove_from_group()
                    self.draw()
                    self.start_sound_tutorial()
                    self.sound_tutorial_active = True

            if pygame.sprite.spritecollideany(self.mouse, self.button_group):
                sprite = pygame.sprite.spritecollide(
                    self.mouse, self.button_group, False
                )
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if sprite[0].id == "exit":
                        self.parent.popState()

            if self.popup_pregunta.activo and not self.popup_help.activo:
                self.popup_respuesta = PopUp(
                    self.parent,
                    ("Respuesta "),
                    "Aceptar",
                    self.arrow_img,
                    self.popup_group,
                )
                self.popup_pregunta.handle_events(evento)
                if self.teclasPulsadas[pygame.K_1] and self.prop_collision:
                    self.evaluate_answer(0)
                elif self.teclasPulsadas[pygame.K_2] and self.prop_collision:
                    self.evaluate_answer(1)
                elif self.teclasPulsadas[pygame.K_3] and self.prop_collision:
                    self.evaluate_answer(2)
                elif self.popup_pregunta.get_click_result() != -1:
                    self.evaluate_answer(self.popup_pregunta.get_click_result())

            if self.popup_respuesta.activo and not self.popup_help.activo:
                self.popup_pregunta.handle_events(evento)
                self.popup_respuesta.handle_events(evento)
                self.popup_pregunta.activo = False
                self.farmer.busy = True
                if (
                    self.teclasPulsadas[pygame.K_RETURN]
                    or self.popup_respuesta.get_click_result() != -1
                ):
                    if self.answer == 1:
                        self.update_character()
                        self.popup_respuesta.remove_from_group()
                        self.popup_pregunta.remove_from_group()
                    elif self.answer == 0:
                        self.popup_pregunta.activo = True
                        self.speak_answers(
                            self.preguntas.dic_pre[self.preguntas.value],
                            self.preguntas.dic_res[self.preguntas.value],
                            True,
                        )
                        self.popup_respuesta.remove_from_group()
                    self.farmer.busy = False
                    self.answer = 2

            if self.popup_final1.activo:
                self.farmer.busy = True
                self.popup_final1.handle_events(evento)
                if (
                    self.teclasPulsadas[pygame.K_RETURN]
                    or self.popup_final1.get_click_result() != -1
                ):
                    self.popup_final1.remove_from_group()
                    self.farmer.busy = False
                    self.level = 2

        if not self.popup_help.activo and not self.completed:
            self.farmer.update()
        self.detect_prop_collision()
        self.check_marker_collision()
        if self.parent.config.is_screen_reader_enabled():
            self.update_markers()
        self.tick_timer()
        self.update_logic()

    def update(self):
        """Trigger a level transition when the level flag is set."""
        if self.level == 1:
            self.start_level1()
            self.level = 0
        elif self.level == 2:
            self.start_level2()
            self.level = 0

    def tick_timer(self):
        """Advance the instruction timer and fire TTS and sound cues at the defined time intervals."""
        if self.timer_started and not self.timer_done:
            if self.current_level == 1:
                self.farmer.busy = True
                if self.elapsed_ms > 21000:
                    self.elapsed_ms = 0
                    self.hint_active = False
                    self.timer_done = True
                    self.farmer.busy = False
                else:
                    self.elapsed_ms += self.timer_clock.get_time()

                if self.elapsed_ms in range(1033, 1066):
                    self.hint_active = True
                    self.speech_server.processtext(
                        "Este sonido te indica que vas por el camino correcto. ",
                        self.parent.config.is_screen_reader_enabled(),
                    )

                elif self.elapsed_ms in range(6000, 6033):
                    self.farmer.sonido_caminar.play(5)

                elif self.elapsed_ms in range(8000, 8033):
                    self.speech_server.processtext(
                        "Este sonido te indica que has encontrado un obstáculo. ",
                        self.parent.config.is_screen_reader_enabled(),
                    )

                elif self.elapsed_ms in range(13000, 13033):
                    self.farmer.sonido_choque.play(5)

                elif self.elapsed_ms in range(14000, 14033):
                    self.speech_server.processtext(
                        "Te encuentras en el primer nivel, muévete hacia la derecha para comenzar. ",
                        self.parent.config.is_screen_reader_enabled(),
                    )

            elif self.current_level == 2:
                self.farmer.busy = True
                if self.elapsed_ms > 13000:
                    self.elapsed_ms = 0
                    self.hint_active = False
                    self.timer_done = True
                    self.farmer.busy = False
                    self.marker_group.add(
                        self.marker_seed_cart, self.marker_can, self.marker_fertilizer, self.marker_insect
                    )
                else:
                    self.elapsed_ms += self.timer_clock.get_time()

                if self.elapsed_ms in range(1033, 1066):
                    self.hint_active = True
                    self.speech_server.processtext(
                        "Te encuentras en el nivel 2. Busca la carretilla "
                        "y luego recolecta los elementos necesarios para la siembra. ",
                        self.parent.config.is_screen_reader_enabled(),
                    )

    def update_logic(self):
        """Evaluate win conditions and manage state transitions for levels 1 and 2."""
        if (self.farmer.marker_code == 7 and self.current_level == 1) or (
            self.current_level == 2 and self.farmer.marker_code >= 31
        ):
            if not self.completed:
                self.anim_fondo.add(self.arrow_anim)
                if self.parent.config.is_screen_reader_enabled() and self.narration_pending:
                    self.hint_active = True
                    self.speech_server.processtext(
                        "Has recolectado todos los elementos de este nivel, avanza hasta el sembradío para completar la siembra. ",
                        self.parent.config.is_screen_reader_enabled(),
                    )
                    if self.current_level == 1:
                        self.farmer.relocate(460, 300)
                    elif self.current_level == 2:
                        self.farmer.relocate(460, 260)
                    self.narration_pending = False

        if self.marker and self.parent.config.is_screen_reader_enabled():
            self.check_markers()
        else:
            self.announce_position = False

        if self.prop_collision:
            self.show_question_popup()
        else:
            if not self.hint_active and not self.marker and self.speech_server.hablando:
                self.speech_server.stopserver()

            self.text_visible = False
            self.popup_pregunta.remove_from_group()

        if (
            self.meta.colliderect(self.farmer.char_rect)
            and self.farmer.marker_code == 7
            and self.current_level == 1
        ):
            self.flowers.continuar()
            self.anim_fondo.add(self.planting_anim)
            self.anim_fondo.remove(self.arrow_anim)
            self.character_group.remove(self.farmer)
            self.meta = pygame.Rect(0, 0, 1, 1)
            self.completed = True
            self.hint_active = True
            self.popup_final1.add_to_group()
            self.speech_server.processtext(
                "¡Muy bien! Has finalizado el primer nivel. Pulsa Enter para continuar. ",
                self.parent.config.is_screen_reader_enabled(),
            )

        if (
            self.meta.colliderect(self.farmer.char_rect)
            and self.farmer.marker_code == 31
            and self.current_level == 2
        ):
            self.flowers.continuar()
            self.anim_fondo.add(self.planting_anim)
            self.anim_fondo.remove(self.arrow_anim)
            self.character_group.remove(self.farmer)
            self.meta = pygame.Rect(0, 0, 1, 1)
            self.completed = True
            self.hint_active = True
            self.popup_instructions.remove_from_group()
            self.popup_instructions = PopUp(
                self.parent,
                "    ¡Excelente! Pulsa la tecla ESC o sobre el botón SALIR para ir al menú principal. ",
                "",
                self.img_textos,
                self.popup_group,
                2,
                240,
                440,
                -160,
            )
            self.popup_instructions.add_to_group()
            self.speech_server.processtext(
                "¡Excelente! Pulsa la tecla escape "
                "o sobre el botón active para ir al menú principal. ",
                self.parent.config.is_screen_reader_enabled(),
            )

    def evaluate_answer(self, value):
        """
        Evaluate the selected answer option and show the appropriate feedback popup.

        @param value: Zero-based index of the option chosen by the user.
        @type value: int
        """
        self.cache_click = value
        try:
            question = self.activity1_questions[self.current_question_id]
            answer = question["options"][value]
            if answer == question["correct"]:
                self.answer = 1
                self.popup_respuesta = PopUp(
                    self.parent,
                    (question["hints"][value],),
                    "Aceptar",
                    (self.hint_images[int(self.current_question_id)], self.img_clapping),
                    self.popup_group,
                    0,
                    512,
                    400,
                )
            else:
                self.answer = 0
                self.popup_respuesta = PopUp(
                    self.parent,
                    (question["hints"][value],),
                    "Aceptar",
                    self.img_thinking,
                    self.popup_group,
                    0,
                    512,
                    400,
                )
            self.speech_server.processtext(
                question["hints"][value] + "Pulsa Enter para continuar. ",
                self.parent.config.is_screen_reader_enabled(),
            )
            self.popup_respuesta.add_to_group()
        except:
            print("Valor fuera de rango")

    def get_hint_level1(self):
        """
        Determine the TTS message index for the current position marker in level 1.

        @return: Index into the marker's message list.
        @rtype: int
        """
        if self.current_marker.id == "semilla":
            if self.farmer.marker_code in [0, 2]:
                return 0
            elif self.farmer.marker_code == 1:
                return 1
            else:
                return 2

        elif self.current_marker.id == "regadera":
            if self.farmer.marker_code in [0, 1]:
                return 0
            elif self.farmer.marker_code == 2:
                return 1
            else:
                return 2

        elif self.current_marker.id == "pala":
            if self.farmer.marker_code >= 3:
                return 0
            else:
                return 1

        elif self.current_marker.id in ["semilla1", "regadera1"]:
            return 0

        else:
            return 0

    def get_hint_level2(self):
        """
        Determine the TTS message index for the current position marker in level 2.

        @return: Index into the marker's message list.
        @rtype: int
        """
        if self.current_marker.id == "sem_car":
            if self.farmer.marker_code == -1:
                return 2
            elif self.farmer.marker_code in range(0, 31, 2):
                return 0
            else:
                return 1

        elif self.current_marker.id == "regadera":
            if self.farmer.marker_code in [
                0,
                1,
                4,
                5,
                8,
                9,
                12,
                13,
                16,
                17,
                20,
                21,
                24,
                25,
                28,
                29,
            ]:
                return 0
            elif self.farmer.marker_code in [3, 9, 13, 21, 25]:
                return 1
            else:
                return 2

        elif self.current_marker.id == "pala":
            if self.farmer.marker_code == 27:
                return 0
            else:
                return 1

        elif self.current_marker.id == "abono":
            if self.farmer.marker_code in range(0, 8) or self.farmer.marker_code in range(
                16, 24
            ):
                return 0
            elif self.farmer.marker_code != 19:
                return 1
            else:
                return 2

        elif self.current_marker.id == "insec":
            if self.farmer.marker_code < 16:
                return 0
            elif self.farmer.marker_code not in [3, 7, 11, 15, 19, 23, 27]:
                return 1
            elif self.farmer.marker_code == 19:
                return 2
            else:
                return 3

        elif self.current_marker.id in [
            "abono1",
            "insect1",
            "regadera1",
            "semillas1",
            "carretilla1",
        ]:
            return 0

        else:
            return 0

    def check_markers(self):
        """Request TTS to read the instruction associated with the marker the character is standing on."""
        if not self.announce_position:
            if self.current_level == 1:
                self.speech_server.processtext(
                    self.activity1_data["markers"]["start_level1"][self.current_marker.id][
                        self.get_hint_level1()
                    ],
                    self.parent.config.is_screen_reader_enabled(),
                )
            elif self.current_level == 2:
                self.speech_server.processtext(
                    self.activity1_data["markers"]["start_level2"][self.current_marker.id][
                        self.get_hint_level2()
                    ],
                    self.parent.config.is_screen_reader_enabled(),
                )
            self.announce_position = True

    def speak_answers(self, question, answers, repeat=False):
        """
        Send the question prompt and answer options to the TTS server.

        @param question: Question text for the found object.
        @type question: str
        @param answers: List of answer option strings.
        @type answers: list
        @param repeat: True if re-reading after an incorrect answer; False on first presentation.
        @type repeat: bool
        """
        texto = ""
        for i in answers:
            texto += "opción número:" + i
        if repeat:
            final = (
                "Selecciona la opción que corresponde al siguiente enunciado: "
                + question
                + ":"
                + texto
            )
        else:
            final = (
                "Has encontrado: "
                + self.sprite.nombre
                + "Selecciona la opción que corresponde al siguiente enunciado:"
                + question
                + ":"
                + texto
            )
        self.speech_server.processtext(final, self.parent.config.is_screen_reader_enabled())

    def update_character(self):
        """Update the character's code and sprite image, then remove the collected object from the scene."""
        self.farmer.marker_code += self.sprite.aumento
        if self.current_question_id in self.remaining_question_ids:
            self.remaining_question_ids.remove(self.current_question_id)
        self.farmer.set_image(self.farmer.image_paths[self.farmer.marker_code])
        self.prop_group.remove(self.sprite)
        if self.current_level == 1:
            if self.farmer.marker_code in [1, 3, 5]:
                self.marker_group.add(self.seed_collect_marker)
            if self.farmer.marker_code in [2, 3, 6]:
                self.marker_group.add(self.can_collect_marker)

        if self.current_level == 2:
            if self.farmer.marker_code == 0:
                self.marker_group.add(self.cart_collect_marker)
            if self.farmer.marker_code in range(1, 32, 2):
                self.marker_group.add(self.seed_collect_marker)
            if self.farmer.marker_code not in [
                0,
                1,
                4,
                5,
                8,
                9,
                12,
                13,
                16,
                17,
                20,
                21,
                24,
                25,
                28,
                29,
            ]:
                self.marker_group.add(self.can_collect_marker)
            if self.farmer.marker_code in range(8, 15) or self.farmer.marker_code in range(
                24, 31
            ):
                self.marker_group.add(self.fertilizer_collect_marker)
            if self.farmer.marker_code in range(17, 31):
                self.marker_group.add(self.insect_collect_marker)

    def update_markers(self):
        """Add position markers to the scene when the character reaches the required collection state."""
        if self.current_level == 1:
            if (
                self.farmer.marker_code == 3
                and self.marker_shovel not in self.marker_group.sprites()
            ):
                self.marker_group.add(self.marker_shovel)
                [self.boundaries.remove(i) for i in self.boundaries.sprites() if i.id == 15]
        elif self.current_level == 2:
            if (
                self.farmer.marker_code == 27
                and self.marker_shovel not in self.marker_group.sprites()
            ):
                self.marker_group.add(self.marker_shovel)
                [self.boundaries.remove(i) for i in self.boundaries.sprites() if i.id == 24]

    def show_question_popup(self):
        """Show a question popup for the object the character has collided with.

        In level 2 the popup only appears after the wheelbarrow has been collected."""
        if not self.text_visible:
            if self.farmer.marker_code >= 0 or self.sprite.nombre == "la carretilla. ":
                if not self.remaining_question_ids:
                    return
                r1 = random.randint(0, len(self.remaining_question_ids) - 1)
                qid = self.remaining_question_ids[r1]
                question = self.activity1_questions[qid]
                self.speak_answers(
                    question["prompt"],
                    question["options_reader"],
                )
                self.current_question_id = qid
                self.popup_pregunta = PopUp(
                    self.parent,
                    tuple(question["popup"]),
                    "Aceptar",
                    0,
                    self.popup_group,
                    1,
                )
                self.popup_pregunta.add_to_group()
                self.text_visible = True

    def detect_prop_collision(self):
        """Detect collision between the character and collectible objects and set the collision flag."""
        if self.farmer.char_rect.collidelist(self.prop_group.sprites()) != -1:
            self.sprite = self.prop_group.sprites()[
                self.farmer.char_rect.collidelist(self.prop_group.sprites())
            ]
            self.prop_collision = True
        else:
            self.prop_collision = False

    def check_marker_collision(self):
        """Detect collision between the character and position markers and set the marker flag."""
        if self.farmer.rect.collidelist(self.marker_group.sprites()) != -1:
            self.current_marker = self.marker_group.sprites()[
                self.farmer.rect.collidelist(self.marker_group.sprites())
            ]
            self.marker = True
        else:
            self.marker = False

    def animate_background(self):
        """Scroll the cloud sprite to simulate continuous background movement."""
        self.clouds.rect.move_ip(self.cloud_speed, 0)
        if self.clouds.rect.left + self.clouds.rect.width + 100 < 0:
            self.clouds.move(1024)

    def draw_debug_rects(self, lista):
        """
        Draw debug rectangles for a list of objects.

        @param lista: List of objects that have a rect attribute.
        @type lista: list
        """
        for i in lista:
            pygame.draw.rect(self.canvas, (255, 0, 0), i, 1)

    def draw(self):
        """Draw the background and all sprite groups onto the display surface."""
        self.animate_background()
        self.mouse.update()
        self.canvas.blit(self.background, (0, 0))
        self.anim_fondo.draw(self.canvas)
        self.prop_image_group.draw(self.canvas)
        self.prop_group.draw(self.canvas)
        self.button_group.draw(self.canvas)
        self.character_group.draw(self.canvas)
        # self.draw_debug_rects(self.marker_group.sprites())
        # self.draw_debug_rects(self.boundaries.sprites())
        # pygame.draw.rect(self.canvas, (255, 0, 0), self.farmer.char_rect, 1)
        # pygame.draw.rect(self.canvas, (255, 0, 0), self.farmer.rect, 1)
        # pygame.draw.rect(self.canvas, (255, 0, 0), self.meta, 1)
        self.popup_group.draw(self.canvas)

    def start(self):
        pass

    def cleanUp(self):
        pass
