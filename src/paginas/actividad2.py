#!/usr/bin/env python

import pygame

from components import screen
from components.textoci import InlineText
from components.textbox import TextBox
from components.popups import PopUp, TextButton
from components.animations import Animation
from paginas import pantalla2


class Activity(screen.Screen):
    """Three-level maths activity screen where the student solves plant-themed arithmetic problems."""

    def __init__(self, parent):
        """
        Initialise the activity: load assets, build popups, and load level 1.

        @param parent: Screen manager instance.
        @type parent: Manejador
        """
        self.parent = parent
        self.screen = self.parent.screen
        self.text_group = pygame.sprite.Group()
        self.card_group = pygame.sprite.Group()
        self.menu2 = pygame.image.load(self.misc_path + "fondoact3.png").convert()
        self.menu3 = self.menu2.subsurface((666, 0, 358, 572))
        self.background = pygame.image.load(self.misc_path + "fondoact3.png").convert()
        self.keyboard_active = 0
        self.check_btn = TextButton("boton", self.parent, "Comprobar")
        self.text_button_group.add(self.check_btn)
        self.img1 = pygame.image.load(self.popups_path + "enter.png")
        img2 = pygame.image.load(self.popups_path + "tab.png")
        img3 = pygame.image.load(self.popups_path + "f1.png")
        img4 = pygame.image.load(self.popups_path + "esc.png")
        img5 = pygame.image.load(self.popups_path + "f2.png")
        self.popup_correct = PopUp(
            self.parent, ("prueba",), "Aceptar", self.img1, self.popup_group
        )
        self.popup_wrong = PopUp(
            self.parent, ("prueba",), "Aceptar", self.img1, self.popup_group
        )
        self.instruction1 = "    Pulsa la tecla F1 para ver las instrucciones. "
        self.narration = (
            "    Instrucciones: resuelve los siguientes problemas y verifica la respuesta colocándola en el recuadro. "
            "La tecla F2 activa o desactiva la ayuda. "
            "ESCAPE te permitirá regresar al menú. "
            "Pulsa la tecla F1 para process la actividad. "
        )
        self.img_clapping = pygame.image.load(
            self.popups_path + "aplaudiendo.png"
        ).convert_alpha()
        self.img_thinking = pygame.image.load(
            self.popups_path + "pensando.png"
        ).convert_alpha()
        self.img_empty = pygame.image.load(
            self.misc_path + "cuadro-narration-popup.png"
        ).convert_alpha()
        self.img_sprouter = pygame.image.load(
            self.popups_path + "img_sprouter.png"
        ).convert_alpha()
        self.dic = {
            "ENTER": self.img1,
            "TABULACIÓN": img2,
            "F1": img3,
            "ESCAPE": img4,
            "F2": img5,
        }
        self.popup_instruction_fixed = PopUp(
            self.parent,
            self.instruction1,
            "Aceptar",
            self.dic,
            self.popup_group,
            2,
            845,
            90 + self.parent.config.get_font_size(),
            -280,
        )
        self.popup_help = PopUp(
            self.parent,
            self.narration,
            "Aceptar",
            self.dic,
            self.popup_group,
            2,
            512,
            281,
            100,
        )
        self.hint_text = "    Calcula el número total de flores que puedes armar en paquetes de 25 flores. "
        self.popup_empty = PopUp(
            self.parent, (self.instruction1,), "Aceptar", self.img1, self.popup_group
        )
        self.popup_instruction = PopUp(
            self.parent,
            self.hint_text,
            "Aceptar",
            self.dic,
            self.popup_group,
            2,
            512,
            281,
        )
        self.popup_instruction_fixed.add_to_group()
        self.popup_help.add_to_group()
        self.instruction_flag = 0
        self.start_level1()
        self.loaded_level = 0

    def start_level1(self):
        """Load assets and initialise the question text and input field for level 1."""
        self.level = 1
        self.close_btn = pygame.sprite.Sprite()
        self.close_btn.image = pygame.image.load(
            self.misc_path + "cerrar.png"
        ).convert_alpha()
        self.close_btn.rect = self.close_btn.image.get_rect()
        self.close_btn.rect.move_ip(610, 11)
        self.table_button = pygame.sprite.Sprite()
        self.table_button.image = pygame.image.load(
            self.misc_path + "mesa.png"
        ).convert_alpha()
        self.table_button.rect = ((0, 415), self.table_button.image.get_size())
        self.help_btn = pygame.sprite.Sprite()
        self.help_btn.image = pygame.image.load(
            self.misc_path + "ayuda.png"
        ).convert_alpha()
        self.help_btn.rect = self.help_btn.image.get_rect()
        self.help_btn.rect.move_ip(985, 500)
        self.text_box_sprite = pygame.sprite.Sprite()
        self.text_box_sprite.image = pygame.image.load(
            self.misc_path + "cuadro-narration.png"
        ).convert()
        self.text_box_sprite.rect = self.text_box_sprite.image.get_rect()
        self.card_group.add(
            self.help_btn, self.close_btn, self.text_box_sprite, self.table_button
        )
        animacion1 = animation_index(
            "anim1", self.misc_path + "reloj.png", 5, 1, 446, 38, None, True, 100
        )
        animacion2 = animation_index(
            "anim2", self.misc_path + "obreros.png", 6, 1, -76, -39, None, True, 6
        )
        animacion3 = animation_index(
            "anim3", self.misc_path + "caja.png", 8, 1, 520, 355, None, True, 36
        )
        self.anim_group.add(animacion1, animacion2, animacion3)
        self.question = (
            "    Los trabajadores de una floristería tienen que empacar 3.215 flores en paquetes de 25 flores cada uno. "
            "¿Cuántas flores sobran después de armar todos los paquetes? "
        )
        self.pregunta_l = (
            "    Los trabajadores de una floristería tienen que empacar 3215 flores en paquetes de 25 flores cada uno. "
            "¿Cuántas flores sobran después de armar todos los paquetes? "
        )
        narration = InlineText(
            700,
            self.popup_instruction_fixed.extra_width,
            self.question,
            self.parent.config.get_font_size(),
            1,
            985,
            0,
        )
        self.text_group.add(narration.words)
        self.text_box_sprite.rect.move_ip(
            725,
            self.popup_instruction_fixed.extra_width
            + narration.final_width
            + self.parent.config.get_font_size()
            - 5,
        )
        self.intr_texto = TextBox(
            730,
            self.popup_instruction_fixed.extra_width
            + narration.final_width
            + self.parent.config.get_font_size(),
            "15",
            self.screen,
            "medium",
        )
        self.check_btn.set_center(
            666 + (self.menu3.get_rect().w / 2),
            self.popup_instruction_fixed.extra_width + narration.final_width + 80,
        )
        self.success_text = "    ¡Muy bien! Sabías que... un trozo de tallo verde que sea introducido en la tierra para multiplicar una planta tiene por nombre esqueje. "
        self.error_text = "    Recuerda: si se reparte de forma equitativa las flores, podrás saber cuantas cajas lograrás armar. "
        self.empty_text = "    Para continuar deberás contestar correctamente la question. Si la casilla queda vacía no podrás avanzar al siguiente problema. "
        self.hint_text = "    Calcula el número total de flores que puedes armar en paquetes de 25 flores. "
        self.speech_server.processtext(self.narration, self.parent.config.is_screen_reader_enabled())
        if self.keyboard_active == 0:
            self.keyboard_active = True

    def start_level2(self):
        """Load assets and initialise the question text and input field for level 2."""
        pygame.event.clear
        self.level = 2
        self.card_group.remove(self.table_button)
        self.text_group.empty()
        self.anim_group.empty()
        animacion1 = animation_index(
            "anim0_1", self.misc_path + "animacion4.png", 10, 1, -40, 0, None, True, 25
        )
        self.anim_group.add(animacion1)
        self.background = pygame.image.load(self.misc_path + "fondoact4.png").convert()
        self.question = "    En una cesta hay 60 sobres de semillas, de ellos 1/5 son de pimentón, 1/2 son de girasol y el resto de perejil. ¿Cuántos sobres son de semillas de perejil? "
        narration = InlineText(
            700,
            self.popup_instruction_fixed.extra_width,
            self.question,
            self.parent.config.get_font_size(),
            1,
            985,
        )
        self.text_group.add(narration.words)
        self.pregunta_lector = "    En una cesta hay 60 sobres de semillas, de ellos un quinto son de pimentón, un medio son de girasol y el resto de perejil. ¿Cuántos sobres son de semilla de perejil? "
        self.text_box_sprite.rect.y = (
            self.popup_instruction_fixed.extra_width
            + narration.final_width
            + self.parent.config.get_font_size()
            - 5
        )
        self.intr_texto = TextBox(
            730,
            self.popup_instruction_fixed.extra_width
            + narration.final_width
            + self.parent.config.get_font_size(),
            "18",
            self.screen,
            "medium",
        )
        self.check_btn.set_center(
            666 + (self.menu3.get_rect().w / 2),
            self.popup_instruction_fixed.extra_width + narration.final_width + 80,
        )
        self.success_text = "    ¡Excelente! Para evitar la deforestación y contribuir con el cuidado del ambiente, cuando vayas de visita a los parques recoge los desechos que te hayan quedado durante tu visita. "
        self.error_text = (
            "    Recuerda: un sobre esta representado en fracciones como 1/60. "
        )
        self.error_text_reader = (
            "    Recuerda: un sobre está representado en fracciones como 1 entre 60. "
        )
        self.empty_text = "    Para continuar deberás contestar correctamente la question. Si la casilla queda vacía no podrás avanzar al siguiente problema. "
        self.hint_text = "    Al construir la ecuación utiliza los 60 sobres como la unidad. Luego de hallar el valor en fracciones transformala a números naturales. "
        self.loaded_level = 1
        self.speech_server.processtext(
            "problema número 2:"
            + self.pregunta_lector
            + "escribe tu respuesta y utiliza la tecla ENTER para confirmar",
            self.parent.config.is_screen_reader_enabled(),
        )
        if self.keyboard_active == 0:
            self.keyboard_active = True

    def start_level3(self):
        """Load assets and initialise the question text and input field for level 3."""
        pygame.event.clear
        self.level = 3
        self.text_group.empty()
        self.anim_group.empty()
        self.anim_group.empty()
        self.background = pygame.image.load(self.misc_path + "fondoact5.png").convert()
        animacion1 = animation_index(
            "anim_1", self.misc_path + "animacion5.png", 6, 1, -30, 44, None, True, 25
        )
        self.anim_group.add(animacion1)
        self.question = "  Una distribuidora de flores recibió 12.831 bolívares por concepto de las ventas durante el mes de marzo. Si vendieron 987 flores, ¿Cuál es el costo de cada flor? "
        self.pregunta_l = "  Una distribuidora de flores recibió 12831 bolívares por concepto de las ventas durante el mes de marzo. Si vendieron 987 flores, ¿Cuál es el costo de cada flor? "
        narration = InlineText(
            700,
            self.popup_instruction_fixed.extra_width,
            self.question,
            self.parent.config.get_font_size(),
            1,
            985,
        )
        self.text_group.add(narration.words)
        self.text_box_sprite.rect.y = (
            self.popup_instruction_fixed.extra_width
            + narration.final_width
            + self.parent.config.get_font_size()
            - 5
        )
        self.intr_texto = TextBox(
            730,
            self.popup_instruction_fixed.extra_width
            + narration.final_width
            + self.parent.config.get_font_size(),
            "13",
            self.screen,
            "medium",
        )
        self.check_btn.set_center(
            666 + (self.menu3.get_rect().w / 2),
            self.popup_instruction_fixed.extra_width + narration.final_width + 80,
        )
        self.success_text = "   ¡Muy bien! ¿Has hecho alguna vez un img_sprouter con semillas de caraota? Con la ayuda de tu maestra o maestro investiga los pasos a seguir para que una semilla se reproduzca y se logre obtener una nueva planta. "
        self.error_text = "    Recuerda: debes separar en partes iguales para obtener el valor de cada flor. "
        self.empty_text = "    Para continuar deberás contestar correctamente la question. Si la casilla queda vacía no podrás avanzar al siguiente problema. "
        self.hint_text = "    Existe una operación básica que te permite repartir equitativamente una cantidad entre un cierto número. Es el proceso contrario a la multiplicación. "
        self.speech_server.processtext(
            "problema número 3:"
            + self.question
            + "escribe tu respuesta y utiliza la tecla ENTER para confirmar",
            self.parent.config.is_screen_reader_enabled(),
        )
        if self.keyboard_active == 0:
            self.keyboard_active = True

    def click(self, event):
        """
        Return True if a left mouse button click occurred.

        @param event: Event to inspect.
        @type event: pygame.event.Event

        @return: True if the event is a left-button click; False otherwise.
        @rtype: bool
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pygame.mouse.get_pressed()[0]:
                return True
            else:
                return False

    def handle_popup(self, message_type):
        """
        Show the appropriate feedback popup based on the result type.

        @param message_type: Result type; one of "bien" (correct), "mal" (wrong), "vacio" (empty), or "instruccion" (hint).
        @type message_type: str
        """
        if not self.popup_wrong.activo or not self.popup_correct.activo:
            if message_type == "bien":
                self.speech_server.stopserver()
                if self.level == 3:
                    self.speech_server.processtext(
                        self.success_text
                        + "Terminaste todos los problemas! Pulsa enter para back al menú del recurso.",
                        self.parent.config.is_screen_reader_enabled(),
                    )
                    self.popup_correct = PopUp(
                        self.parent,
                        (self.success_text,),
                        "Aceptar",
                        (self.img_sprouter, self.img_clapping),
                        self.popup_group,
                    )

                else:
                    self.speech_server.processtext(
                        self.success_text
                        + "Pulsa enter para pasar al siguiente problema. ",
                        self.parent.config.is_screen_reader_enabled(),
                    )
                    self.popup_correct = PopUp(
                        self.parent,
                        (self.success_text,),
                        "Aceptar",
                        self.img_clapping,
                        self.popup_group,
                    )

                self.popup_correct.add_to_group()

            elif message_type == "mal":
                self.popup_wrong = PopUp(
                    self.parent,
                    (self.error_text,),
                    "Aceptar",
                    self.img_thinking,
                    self.popup_group,
                )
                self.popup_wrong.add_to_group()
                self.speech_server.stopserver()
                if self.level == 2:
                    self.speech_server.processtext(
                        "tu respuesta es: "
                        + self.intr_texto.palabra_f
                        + self.error_text_reader
                        + "Pulsa enter para continuar",
                        self.parent.config.is_screen_reader_enabled(),
                    )
                    self.intr_texto.reset()
                else:
                    self.speech_server.processtext(
                        "tu respuesta es: "
                        + self.intr_texto.palabra_f
                        + self.error_text
                        + " Pulsa enter para continuar",
                        self.parent.config.is_screen_reader_enabled(),
                    )
                    self.intr_texto.reset()

            elif message_type == "vacio":
                self.popup_empty = PopUp(
                    self.parent,
                    (self.empty_text,),
                    "Aceptar",
                    self.img_empty,
                    self.popup_group,
                )
                self.popup_empty.add_to_group()
                self.speech_server.stopserver()
                self.speech_server.processtext(
                    self.empty_text + "Pulsa enter para continuar",
                    self.parent.config.is_screen_reader_enabled(),
                )

            elif message_type == "instruccion":
                if self.popup_instruction.activo:

                    self.speech_server.stopserver()
                    self.popup_instruction.remove_from_group()
                    if self.level == 2:
                        self.speech_server.processtext(
                            self.pregunta_lector
                            + "escribe tu respuesta y utiliza la tecla ENTER para confirmar",
                            self.parent.config.is_screen_reader_enabled(),
                        )
                    else:
                        self.speech_server.processtext(
                            self.pregunta_l
                            + "escribe tu respuesta y utiliza la tecla ENTER para confirmar",
                            self.parent.config.is_screen_reader_enabled(),
                        )

                else:
                    self.popup_instruction = PopUp(
                        self.parent,
                        self.hint_text,
                        "Aceptar",
                        self.dic,
                        self.popup_group,
                        2,
                        512,
                        281,
                    )
                    self.popup_instruction.add_to_group()
                    self.speech_server.stopserver()
                    self.speech_server.processtext(
                        self.hint_text + "Pulsa F2 para continuar.",
                        self.parent.config.is_screen_reader_enabled(),
                    )

    def evaluador(self):
        """Validate the text-box answer and call handle_popup() with the appropriate result."""
        if self.intr_texto.check_answer():
            self.handle_popup("bien")

        elif self.intr_texto.is_empty():
            self.handle_popup("vacio")

        elif not self.intr_texto.check_answer():
            self.handle_popup("mal")

    def update(self):
        """Update sprite groups and redraw the screen."""

        self.intr_texto.blink_cursor()
        self.intr_texto.add_to_group(self.text_box_group)
        self.screen.blit(self.background, (0, 0))
        self.anim_group.draw(self.screen)
        self.parent.screen.blit(self.menu3, (666, 0))
        self.card_group.draw(self.screen)
        self.text_group.draw(self.screen)
        self.text_button_group.draw(self.screen)
        self.text_box_group.draw(self.screen)
        self.popup_group.draw(self.screen)
        self.draw_debug_rectangles()

    def handleEvents(self, events):
        """
        Process input events for this screen.

        @param events: Event list from the main loop.
        @type events: list
        """
        teclasPulsadas = pygame.key.get_pressed()
        for event in events:
            if event.type == pygame.QUIT:
                self.parent.quit()

            if (
                not self.popup_correct.activo
                and not self.popup_wrong.activo
                and not self.popup_empty.activo
            ):

                if self.keyboard_active == 0:
                    self.keyboard_active = True
            if self.popup_correct.activo:
                self.popup_correct.handle_events(event)
                if not self.popup_correct.get_click_result():
                    self.speech_server.stopserver()
                    if self.level == 1:
                        self.start_level2()
                    elif self.level == 2:
                        self.start_level3()
                    elif self.level == 3:
                        self.clear_groups()
                        self.parent.pushState(pantalla2.Screen(self.parent))

            if self.popup_wrong.activo:
                self.popup_wrong.handle_events(event)
                if not self.popup_wrong.get_click_result():
                    self.speech_server.stopserver()
                    if self.level == 2:
                        self.speech_server.processtext(
                            self.pregunta_lector
                            + "escribe tu respuesta y utiliza la tecla ENTER para confirmar",
                            self.parent.config.is_screen_reader_enabled(),
                        )
                    else:
                        self.speech_server.processtext(
                            self.pregunta_l
                            + "escribe tu respuesta y utiliza la tecla ENTER para confirmar",
                            self.parent.config.is_screen_reader_enabled(),
                        )

            if self.popup_empty.activo:
                self.popup_empty.handle_events(event)
                pygame.event.clear()
                if not self.popup_empty.get_click_result():
                    self.speech_server.stopserver()
                    if self.level == 2:
                        self.speech_server.processtext(
                            self.pregunta_lector
                            + "escribe tu respuesta y utiliza la tecla ENTER para confirmar",
                            self.parent.config.is_screen_reader_enabled(),
                        )
                    else:
                        self.speech_server.processtext(
                            self.pregunta_l
                            + "escribe tu respuesta y utiliza la tecla ENTER para confirmar",
                            self.parent.config.is_screen_reader_enabled(),
                        )

            if teclasPulsadas[pygame.K_ESCAPE]:
                self.clear_groups()
                self.parent.pushState(pantalla2.Screen(self.parent))

            if self.click(event):

                if (
                    not self.popup_help.activo
                    and not self.popup_correct.activo
                    and not self.popup_wrong.activo
                ):

                    if not self.popup_instruction.activo:
                        if self.text_box_sprite.rect.collidepoint(
                            pygame.mouse.get_pos()
                        ):
                            self.keyboard_active = True
                        else:
                            self.keyboard_active = False

                        if self.check_btn.rect.collidepoint(pygame.mouse.get_pos()):
                            self.evaluador()

                    if self.help_btn.rect.collidepoint(pygame.mouse.get_pos()):
                        self.handle_popup("instruccion")

                if self.close_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    self.clear_groups()
                    self.parent.pushState(pantalla2.Screen(self.parent))

            if event.type == pygame.KEYDOWN:
                if teclasPulsadas[pygame.K_TAB]:
                    if (
                        not self.popup_instruction.activo
                        and not self.popup_help.activo
                        and not self.popup_correct.activo
                        and not self.popup_wrong.activo
                    ):
                        if self.keyboard_active == 0:
                            self.keyboard_active = True

                            if self.intr_texto.is_empty():
                                self.speech_server.stopserver()
                                self.speech_server.processtext(
                                    "escribe los números que corresponden a la respuesta correcta.",
                                    self.parent.config.is_screen_reader_enabled(),
                                )
                            else:
                                self.speech_server.stopserver()
                                self.speech_server.processtext(
                                    "has escrito el número: "
                                    + self.intr_texto.palabra_f,
                                    self.parent.config.is_screen_reader_enabled(),
                                )

                if teclasPulsadas[pygame.K_F2]:
                    if (
                        not self.popup_help.activo
                        and not self.popup_correct.activo
                        and not self.popup_wrong.activo
                    ):
                        self.handle_popup("instruccion")

                if teclasPulsadas[pygame.K_SPACE]:
                    self.speech_server.repetir()

                if teclasPulsadas[pygame.K_F1]:
                    self.speech_server.stopserver()
                    if self.popup_help.activo:
                        self.popup_help.remove_from_group()
                        if not self.instruction_flag:
                            self.speech_server.stopserver()
                            self.speech_server.processtext(
                                self.pregunta_l
                                + "escribe tu respuesta y utiliza la tecla ENTER para confirmar",
                                self.parent.config.is_screen_reader_enabled(),
                            )
                            self.instruction_flag = 1
                        if self.popup_help.activo:
                            self.popup_help.remove_from_group()
                    else:
                        self.speech_server.processtext(
                            self.narration, self.parent.config.is_screen_reader_enabled()
                        )
                        self.popup_help.add_to_group()

            if self.intr_texto.process(event, self.keyboard_active):
                self.evaluador()
                self.keyboard_active = 0

    def draw(self):
        pass

    def start(self):
        pass

    def pause(self):
        pass

    def cleanUp(self):
        pass
