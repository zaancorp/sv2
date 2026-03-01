#!/usr/bin/env python

import pygame

from librerias.animations import Animation, RenderAnim
from librerias.image import Image
from librerias.cursor import cursor
from librerias.button import Button, RenderButton
from librerias.speechserver import Speechserver
from librerias.magnificador import magnificador, Rendermag
from librerias.texto import Text
from librerias.assets_data import (
    backgrounds as _backgrounds,
    banners as _banners,
    images as _images,
    animations as _animations,
    buttons as _buttons,
)


class Pantalla(object):
    """
    Esta clase es una plantilla con atributos y funciones comunes para las pantallas que componen el ReDA
    "Sembrando para el futuro".
    """

    # Shared resources — one instance for the entire application lifetime.
    # Intentionally class-level: the TTS server, cursor, and magnifier are
    # shared singletons that must not be recreated on every screen transition.
    spserver = Speechserver()
    raton = cursor()
    obj_magno = magnificador()

    # Immutable path constants.
    pops = "./imagenes/png/popups/"
    animations_path = "./imagenes/png/animations/"
    backgrounds_path = "./imagenes/png/backgrounds/"
    banners_path = "./imagenes/png/banners/"
    buttons_path = "./imagenes/png/buttons/"
    varios = "./imagenes/png/varios/"

    def __init__(self, parent, screen_id):
        self.parent = parent
        self.load_background(screen_id)
        self.previa = True
        self.reloj_anim = pygame.time.Clock()
        self.reloj_anim.tick(30)

        # Per-screen navigation state — reset fresh for every new screen.
        self.x = ""
        self.anim_actual = 0
        self.elemento_actual = -1
        self.numero_elementos = 0
        self.lista_final = []
        self.lista_botones = []
        self.lista_palabra = []
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.enable = False
        self.entrada_primera_vez = True
        self.deteccion_movimiento = False

        # Per-screen sprite groups — each screen gets its own fresh groups so
        # that pushed/popped screens never corrupt each other's sprite state.
        self.grupo_anim = RenderAnim()
        self.grupo_update = RenderAnim()
        self.grupo_imagen = RenderAnim()
        self.grupo_botones = RenderButton()
        self.grupo_magnificador = Rendermag()
        self.grupo_banner = pygame.sprite.Group()
        self.grupo_tooltip = pygame.sprite.Group()
        self.grupo_cuadro_texto = pygame.sprite.Group()
        self.text_button_group = pygame.sprite.Group()
        self.grupo_mapa = pygame.sprite.OrderedUpdates()
        self.grupo_popup = pygame.sprite.OrderedUpdates()
        self.grupo_fondotexto = pygame.sprite.GroupSingle()
        self.grupo_palabras = pygame.sprite.OrderedUpdates()
        self.debug_groups = [
            self.grupo_imagen,
            self.grupo_botones,
            self.text_button_group,
            self.grupo_banner,
            self.grupo_tooltip,
            self.grupo_popup,
            self.grupo_palabras,
            self.grupo_cuadro_texto,
        ]

    def load_animations(self, animation_ids):
        for id in animation_ids:
            x, y = _animations.get(id).get("coordinates")
            columns = _animations.get(id).get("columns")
            rows = _animations.get(id).get("rows")
            colorkey = _animations.get(id).get("colorkey")
            loop = _animations.get(id).get("loop")
            frames = _animations.get(id).get("frames")
            filename = _animations.get(id).get("filename")
            attribute_name = id.replace("-", "_")
            setattr(
                self,
                attribute_name,
                Animation(
                    id,
                    self.animations_path + filename,
                    columns,
                    rows,
                    x,
                    y,
                    colorkey,
                    loop,
                    frames,
                ),
            )

    def load_background(self, screen_id):
        self.background = pygame.image.load(
            self.backgrounds_path + _backgrounds.get(screen_id)
        ).convert()

    def load_buttons(self, button_ids):
        font_size = self.parent.config.get_font_size()
        for id in button_ids:
            x, y = _buttons.get(id).get("coordinates")
            tooltip = _buttons.get(id).get("tooltip")
            colorkey = _buttons.get(id).get("colorkey")
            loop = _buttons.get(id).get("loop")
            frames = _buttons.get(id).get("frames")
            frame_speed = _buttons.get(id).get("frame_speed")
            filename = _buttons.get(id).get("filename")
            attribute_name = id.replace("-", "_")
            setattr(
                self,
                attribute_name,
                Button(
                    x,
                    y,
                    id,
                    tooltip,
                    font_size,
                    self.buttons_path + filename,
                    frames,
                    colorkey,
                    loop,
                    frame_speed,
                ),
            )

    def load_banners(self, banner_ids):
        for id in banner_ids:
            x, y = _banners.get(id).get("coordinates")
            filename = _banners.get(id).get("filename")
            attribute_name = id.replace("-", "_")
            setattr(self, attribute_name, Image(x, y, self.banners_path + filename))

    def load_images(self, image_ids):
        for id in image_ids:
            filename = _images.get(id)
            attribute_name = id.replace("-", "_")
            setattr(
                self,
                attribute_name,
                pygame.image.load(self.pops + filename).convert_alpha(),
            )

    def screen_text(self, key):
        """
        Returns the raw string for the given key from this screen's section
        in content.json (i.e. content → self.name → key).

        Use this for TTS / processtext calls instead of the verbose raw dict:
            # before:
            self.parent.text_content["content"][self.name]["text_2"]
            # after:
            self.screen_text("text_2")
        """
        return self.parent.text_loader.get("content", self.name, key)

    def load_screen_texts(self, keys, x=64, y=340, text_type=1, right_limit=960, custom=False):
        """
        Creates Text objects for a list of content.json keys belonging to this
        screen's section, all sharing the same layout parameters.

        Returns a dict mapping each key to its Text object.

        Usage in cargar_textos:
            texts = self.load_screen_texts(["text_2", "text_3", "text_4"])
            self.texto4_2 = texts["text_2"]
            self.texto4_3 = texts["text_3"]
            ...

        Override the defaults for screens that use different coordinates:
            texts = self.load_screen_texts(["text_2"], x=32, right_limit=992)
        """
        content = self.parent.text_loader.screen_content(self.name)
        font_size = self.parent.config.get_font_size()
        return {
            key: Text(x, y, content[key], font_size, text_type, right_limit, custom)
            for key in keys
        }

    def limpiar_grupos(self):
        """Limpia los elementos de una pantalla."""
        self.grupo_banner.empty()
        self.grupo_botones.empty()
        self.text_button_group.empty()
        self.grupo_imagen.empty()
        self.grupo_palabras.empty()
        self.grupo_fondotexto.empty()
        self.grupo_anim.empty()
        self.grupo_mapa.empty()
        self.grupo_tooltip.empty()
        self.grupo_popup.empty()
        self.grupo_cuadro_texto.empty()

    def sonido_on(self):
        """Activa un canal de audio para reproducir efectos de sonido."""
        pygame.mixer.init()
        self.canal_audio = pygame.mixer.Channel(0)
        self.canal_audio.set_endevent(pygame.locals.USEREVENT)

    def minimag(self, evento):
        """Gestiona los eventos del magnificador de pantalla: activar/desactivar el magnificador de pantalla,
        aumentar y disminuir el zoom.

        @param evento: Evento que recibe el magnificador cada vez que la pantalla se actualiza.
        @type evento: pygame.event.Event
        """
        for event in evento:
            if self.parent.config.is_magnifier_enabled():
                (a, b) = pygame.mouse.get_pos()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F5:
                        if self.parent.habilitar == False:
                            self.parent.habilitar = True
                            self.grupo_magnificador.add(self.obj_magno)
                        elif self.parent.habilitar == True:
                            self.parent.habilitar = False
                            self.grupo_magnificador.empty()
                    if event.key == pygame.K_PLUS:
                        self.obj_magno.aumentar()
                    elif event.key == pygame.K_MINUS:
                        self.obj_magno.disminuir()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    evento = True
                else:
                    evento = False
                if (
                    self.obj_magno.rect.collidepoint(pygame.mouse.get_pos())
                    and pygame.mouse.get_pressed()[0]
                ):
                    self.enable = True
                    if evento == False:
                        self.obj_magno.rect.left = a - self.obj_magno.w / 2
                        self.obj_magno.rect.top = b - self.obj_magno.h / 2
                else:
                    self.enable = False

    def definir_rect(self, rect=0):
        """Determina la ubicación y dimensiones del rectángulo que indica el elemento actual de la pantalla
        al usar la navegabilidad por teclado.

        @change: El rectángulo ahora mide 10 pixeles más de ancho y alto.

        @param rect: Contiene las dimensiones y la ubicación del rectángulo que se dibujara. Por defecto su valor
        es 0, lo que indica que el rectángulo no se mostrara en la pantalla.
        @type rect: pygame.Rect
        """
        if rect == 0:
            self.rect = (0, 0, 0, 0)
        else:
            (x, y, w, h) = rect
            self.rect = pygame.Rect(x - 5, y - 5, w + 10, h + 10)

    def dibujar_rect(self):
        pygame.draw.rect(self.parent.screen, (0, 255, 0), self.rect, 3)
        """Dibuja un rectangulo de color verde en la posición y con las dimensiones asignadas en
        'definir_rect()'. """

    def draw(self):
        """
        Dibuja el fondo de pantalla y los elementos pertenecientes a los grupos de sprites sobre la superficie
        del manejador de pantallas.
        """

        self.parent.screen.blit(self.background, (0, 0))
        self.grupo_imagen.draw(self.parent.screen)
        self.grupo_anim.draw(self.parent.screen)
        self.grupo_banner.draw(self.parent.screen)
        self.grupo_botones.draw(self.parent.screen)
        self.grupo_fondotexto.draw(self.parent.screen)
        self.grupo_palabras.draw(self.parent.screen)
        self.grupo_tooltip.draw(self.parent.screen)
        self.grupo_popup.draw(self.parent.screen)
        if self.parent.habilitar:
            self.grupo_magnificador.draw(self.parent.screen, self.enable)
        if self.deteccion_movimiento:
            self.dibujar_rect()
        self.draw_debug_rectangles()

    def draw_debug_rectangles(self):
        if self.parent.DRAW_DEBUG_RECTANGLES:
            debug_rectangles = [
                object.rect for group in self.debug_groups for object in group
            ]
            for rectangle in debug_rectangles:
                pygame.draw.rect(self.parent.screen, (255, 0, 0), rectangle, 3)

    def chequeo_palabra(self, lista):
        """
        Verifica si en el texto que se muestra en la pantalla actual, hay palabras interpretables, de ser así
        las agrega en la lista de palabras.

        @param lista: Texto que se muestra en una pantalla.
        @type lista: list
        """
        self.lista_palabra = []
        [self.lista_palabra.append(i) for i in lista if i.interpretable]

    def chequeo_botones(self, lista):
        """
        Agrega los botones que están presentes en una pantalla en la lista de botones.

        @param lista: Botones presentes en la pantalla.
        @type lista: list
        """
        self.lista_botones = []
        [self.lista_botones.append(j) for j in lista if j.id]

    def chequeo_mascaras(self, grupomask):
        """
        Agrega los mapas colisionables a la lista de mascaras.

        @param grupomask: Lista de los mapas presentes en la pantalla.
        @type grupomask: list
        """
        self.lista_mascaras = []
        [self.lista_mascaras.append(mask) for mask in grupomask]

    def _announce_current(self):
        """
        Announce the current keyboard-navigation element via TTS.

        Each focusable object type (Button, palabra, object_mask) implements
        ``get_reader_text()`` to supply its own TTS string, eliminating the
        need for a tipo_objeto string-dispatch here.
        """
        self.definir_rect(self.x.rect)
        self.spserver.processtext(
            self.x.get_reader_text(),
            self.parent.config.is_screen_reader_enabled(),
        )

    def controlador_lector_evento_K_RIGHT(self):
        """
        Gestiona los eventos que se producen cuando se pulsa la flecha derecha del teclado.
        """
        if self.elemento_actual < self.numero_elementos:
            self.elemento_actual += 1
            if self.elemento_actual >= self.numero_elementos:
                self.elemento_actual = self.numero_elementos - 1
            self.x = self.lista_final[self.elemento_actual]
            self._announce_current()

    def controlador_lector_evento_K_LEFT(self):
        """
        Gestiona los eventos que se producen cuando se pulsa la flecha izquierda del teclado.
        """
        if self.elemento_actual > 0:
            self.elemento_actual -= 1
            if self.elemento_actual <= 0:
                self.elemento_actual = 0
            self.x = self.lista_final[self.elemento_actual]
            self._announce_current()

    def start(self):
        pass

    def cleanUp(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass
