#!/usr/bin/env python

import pygame

from librerias import pantalla
from librerias.texto import Text
from librerias.image import Image

from paginas import menucfg
from paginas import pantalla2
from paginas import pantalla6
from paginas import pantalla10

animations = [
    "animation-5",
    "animation-5-0",
    "animation-5-1",
    "animation-5-2",
    "animation-5-3",
]

banners = [
    "banner-inf",
    "banner-repro",
]

buttons = [
    "home",
    "sig",
    "config",
    "volver",
]


class estado(pantalla.Pantalla):
    def __init__(self, parent, anim_actual=0):
        """
        Método inicializador de la clase.

        @param parent: Instancia del gestor de pantallas.
        @type parent: Manejador
        @param anim_actual: Código de la ultima animación mostrada en esta pantalla.
        @type anim_actual: int
        """

        self.name = "screen_5"
        super().__init__(parent, self.name)

        # Animations

        self.anim_actual = anim_actual

        self.load_animations(animations)
        self.load_banners(banners)
        self.load_buttons(buttons)
        self.cargar_textos()

        # Banners
        self.caja_texto = Image(0, 332, self.backgrounds_path + "caja-texto.png")

        self.grupo_update.add(
            self.animation_5, self.animation_5_0, self.animation_5_1, self.animation_5_2
        )

        self.animation_states = {
            1: (self.animation_5, self.texto5_2, "text_2"),
            2: (self.animation_5_3, None, "anim_1"),
            3: (self.animation_5, self.texto5_3, "text_3"),
            4: (self.animation_5_0, None, "anim_2"),
            5: (self.animation_5, self.texto5_4, "text_4"),
            6: (self.animation_5_1, None, "anim_3"),
            7: (self.animation_5, self.texto5_5, "text_5"),
            8: (self.animation_5_2, None, "anim_4"),
            9: (self.animation_5, self.texto5_6, "text_6"),
        }

        self.button_actions = {
            self.home: self.go_home,
            self.config: self.go_config,
            self.volver: self.go_back,
            self.sig: self.go_next,
        }

        self.resume()

    def cargar_textos(self):
        content = self.parent.text_content["content"][self.name]
        font_size = self.parent.config.get_font_size()
        
        text_config = {
            "text_2": (64, 340),
            "text_3": (64, 340),
            "text_4": (64, 340),
            "text_5": (64, 340),
            "text_6": (64, 340),
        }
        
        self.text_objects = {}
        for key, (x, y) in text_config.items():
            self.text_objects[key] = Text(
                x, y, content[key],
                font_size, "normal", 960, False
            )
        
        self.texto5_2, self.texto5_3, self.texto5_4, self.texto5_5, self.texto5_6 = [
            self.text_objects[f"text_{i}"] for i in range(2, 7)
        ]
        
        self.img_palabras = [text.img_palabras for text in self.text_objects.values()]

    def resume(self):
        """
        Verifica si se realizaron cambios en la configuración. Carga los valores iniciales de esta pantalla.
        """
        if self.parent.config.is_text_change_enabled():
            self.load_buttons(buttons)
            self.cargar_textos()
            self.parent.config.set_text_change_enabled(False)
        self.grupo_anim.add(self.animation_5)
        self.grupo_imagen.add(self.animation_5_3)
        self.grupo_banner.add(self.banner_repro, self.banner_inf)
        self.grupo_botones.add(self.config, self.sig, self.volver, self.home)
        self.animation_5.detener()
        self.animation_5_3.detener()
        self.creado = True
        self.final = False
        self.tiempo = 0
        if self.anim_actual == 0:
            self.anim_actual = 1
        self.spserver.processtext(
            "Pantalla: Reproducción de las plantas.", self.parent.config.is_screen_reader_enabled()
        )
        self.reproducir_animacion(self.anim_actual)
        self.entrada_primera_vez = True

    def handle_quit(self, event):
        if event.type == pygame.QUIT:
            self.parent.quit()

    def handle_keydown(self, event):
        if event.key == pygame.K_ESCAPE:
            self.parent.quit()
        elif event.key in (pygame.K_LEFT, pygame.K_UP):
            self.elemento_actual = (self.elemento_actual - 1) % self.numero_elementos
        elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
            self.elemento_actual = (self.elemento_actual + 1) % self.numero_elementos
        elif event.key == pygame.K_RETURN:
            self.handle_selection()

    def handle_mousebuttondown(self, event):
        if event.button == 1:
            for sprite in self.grupo_palabras:
                if sprite.rect.collidepoint(event.pos):
                    self.ir_glosario()
                    return
            for sprite in self.grupo_botones:
                if sprite.rect.collidepoint(event.pos):
                    self.button_actions.get(sprite, lambda: None)()
                    return

    def handle_selection(self):
        if self.elemento_actual < len(self.lista_palabra):
            self.ir_glosario()
        else:
            button = self.lista_botones[self.elemento_actual - len(self.lista_palabra)]
            self.button_actions.get(button, lambda: None)()

    def go_home(self):
        self.parent.changeState(pantalla2.estado(self.parent))

    def go_config(self):
        self.parent.pushState(menucfg.estado(self.parent))

    def go_back(self):
        self.anim_actual -= 1
        self.reproducir_animacion(self.anim_actual)

    def go_next(self):
        self.anim_actual += 1
        self.reproducir_animacion(self.anim_actual)

    def handleEvents(self, events):
        for event in events:
            self.handle_quit(event)

            if event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mousebuttondown(event)

        self.chequeo_botones(self.grupo_botones)
        self.chequeo_palabra(self.txt_actual)
        self.lista_final = self.lista_palabra + self.lista_botones
        self.numero_elementos = len(self.lista_final)

    def update(self):
        """
        Actualiza la posición del cursor, el magnificador de pantalla en caso de que este activado, los
        tooltip de los botones y animaciones o textos correspondientes.
        """
        self.raton.update()
        self.obj_magno.magnificar(self.parent.screen)
        self.grupo_botones.update(self.grupo_tooltip)
        if self.anim_actual == 1 and not self.parent.config.is_screen_reader_enabled():
            if not self.tiempo < 1000:
                self.grupo_fondotexto.add(self.caja_texto)
                self.grupo_palabras.add(self.texto5_2.img_palabras)
                self.txt_actual = self.texto5_2.img_palabras
                self.chequeo_palabra(self.txt_actual)
                self.animation_5.continuar()
        self.tiempo += self.reloj_anim.get_time()

    def setup_animation(self, animation_obj, text_obj, text_key):
        self.elemento_actual = -1
        self.lista_palabra = []
        self.grupo_anim.empty()
        self.grupo_anim.add(animation_obj)
        self.grupo_fondotexto.empty()
        self.grupo_palabras.empty()
        
        if text_obj:
            self.grupo_fondotexto.add(self.caja_texto)
            self.grupo_palabras.add(text_obj.img_palabras)
            self.txt_actual = text_obj.img_palabras
            self.chequeo_palabra(self.txt_actual)
        
        animation_obj.continuar()
        
        self.spserver.processtext(
            self.parent.text_content["content"][self.name][text_key],
            self.parent.config.is_screen_reader_enabled(),
        )

    def reproducir_animacion(self, animacion):
        if 1 <= animacion <= 9:
            animation_obj, text_obj, text_key = self.animation_states[animacion]
            self.setup_animation(animation_obj, text_obj, text_key)

            if animacion == 1:
                self.grupo_botones.remove(self.volver)
                if self.parent.config.is_screen_reader_enabled() and self.entrada_primera_vez:
                    self.spserver.processtext2(
                        self.parent.text_content["content"][self.name]["text_2"],
                        self.parent.config.is_screen_reader_enabled(),
                    )
                    self.entrada_primera_vez = False
            elif animacion == 2:
                self.entrada_primera_vez = False
                self.grupo_botones.empty()
                self.grupo_botones.add(self.config, self.volver, self.sig, self.home)
                self.animation_5.detener()
                self.animation_5_3.update()
                self.animation_5_3.stop = False
            elif animacion == 9:
                self.grupo_botones.add(self.volver)

        elif animacion == 10:
            self.limpiar_grupos()
            self.parent.changeState(pantalla6.estado(self.parent))

        self.chequeo_botones(self.grupo_botones)
        self.lista_final = self.lista_palabra + self.lista_botones
        self.numero_elementos = len(self.lista_final)

    def ir_glosario(self):
        self.parent.pushState(pantalla10.estado(self.parent))
