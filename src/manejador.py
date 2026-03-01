#!/usr/bin/env python

import gc
import sys
import pygame
import subprocess

from librerias.singleton import Singleton
from librerias.magnificador import Rendermag
from librerias.configuration import Configuration
from librerias.text_repository import load_text_content
from librerias.text_loader import TextLoader


class Manejador(metaclass=Singleton):
    """
    Esta clase consiste en una implementación del patrón estrategia para python.
    La instancia de esta clase funciona como un manejador de estados y permite hacer cambios entre pantallas
    que comparten la misma estructura, atributos y métodos.
    """

    habilitar = False
    DRAW_DEBUG_RECTANGLES = False
    VOLVER_PANTALLA_PREVIA = False
    config = Configuration()
    grupo_magnificador = Rendermag()
    rutas_int = [
        "/opt/blender/blenderplayer",
        "blenderplayer",
        "/usr/bin/blenderplayer",
    ]

    def __init__(self, titulo, size=(1024, 572), fullscreen=False):
        """
        Método inicializador de la clase.

        @param titulo: Define el titulo que aparecera en la ventana de la aplicación.
        @type titulo: str
        @param size: Indica la resolución de la ventana de la aplicación. Por defecto es (1024x572).
        @type size: tuple
        @param fullscreen: Si es True la aplicación se mostrara en pantalla completa, si es False en una ventana.
        @type fullscreen: bool
        """
        pygame.init()
        self.primera_vez = True
        self.animacion = 0
        self.pantalla = 0
        self.states = []
        self.running = True
        self.screen = pygame.display.set_mode(size)
        self.load_text_content()
        pygame.display.set_caption(titulo)
        icon = pygame.image.load("./iconos/sembrando96x96.png")
        pygame.display.set_icon(icon)

    def cleanUp(self):
        """
        Limpia los elementos de las pantallas que esten cargadas, desconecta el servicio del sintetizador de voz
        verifica si blenderplayer esta activo, de ser asi lo cierra y finalmente cierra la aplicación.
        """
        self.states[-1].spserver.stopserver()
        self.states[-1].spserver.quitserver()
        while len(self.states) > 0:
            state = self.states.pop()
            state.cleanUp()
        if not subprocess.call(["pgrep", "blenderplayer"]):
            subprocess.call(["pkill", "-9", "blenderplayer"])
        print("Cerrando servidor de texto a voz")
        sys.exit(0)

    def changeState(self, gameState):
        """
        Limpia los elementos de la pantalla actual y carga una nueva pantalla.
        @param gameState: Pantalla que se desea cargar.
        @type gameState: estado
        """
        if len(self.states) > 0:
            state = self.states.pop()
            state.cleanUp()
        self.states.append(gameState)
        self.states[-1].start()
        gc.collect()

    def pushState(self, gameState):
        """
        Carga los elementos de una nueva pantalla sin limpiar la pantalla actual.
        @param gameState: Pantalla que se desea cargar.
        @type gameState: estado
        """
        if len(self.states) > 0:
            self.states[-1].pause()
        self.states.append(gameState)
        self.states[-1].start()

    def popState(self):
        """
        Limpia los elementos de la pantalla actual.
        """
        if len(self.states) > 0:
            state = self.states.pop()
            state.cleanUp()
        if len(self.states) > 0:
            self.states[-1].resume()

    def handleEvents(self, events):
        """
        LLama al metodo handleEvents() de la pantalla actual y le envia los eventos que se estan generando.
        @param events: Lista de eventos que se generan cada vez que la pantalla se acutaliza.
        @type events: pygame.event.Event
        """
        self.states[-1].handleEvents(events)

    def update(self):
        """
        LLama al metodo update() de la pantalla actual.
        """
        self.states[-1].update()

    def draw(self):
        """
        LLama al metodo draw() de la pantalla actual y mantiene la aplicación actualizandose a 30 imágenes
        por segundo.
        """
        self.states[-1].draw()
        self.states[-1].reloj_anim.tick(30)
        pygame.display.flip()

    def quit(self):
        """
        Indica que se debe cerrar la aplicación.
        """
        self.running = False

    def interpretar(self, codigo):
        """
        Dispatcher: lanza el intérprete virtual de lengua de señas (Blenderplayer) cuando la
        accesibilidad auditiva está activada, o muestra el glosario en caso contrario.
        """
        if self.config.get_preference("disc_audi", False):
            self._launch_interpreter(codigo)
        else:
            self._show_glossary(codigo)

    def _launch_interpreter(self, codigo):
        """
        Lanza el subproceso Blenderplayer para interpretar el concepto dado.
        Si Blenderplayer ya está en ejecución, no hace nada.
        """
        running = subprocess.call(["pgrep", "blenderplayer"])
        if running == 1:
            color = self.config.get_preference("color", 0)
            genero = self.config.get_preference("genero", "Hombre")
            velocidad = self.config.get_preference("velocidad", 0.5)
            for ruta in self.rutas_int:
                try:
                    subprocess.Popen(
                        [
                            ruta,
                            "-w",
                            "512",
                            "372",
                            "512",
                            "0",
                            "./interprete/interprete.blend",
                            "-",
                            str(color),
                            str(genero),
                            str(velocidad),
                            str(codigo),
                        ]
                    )
                    pygame.time.delay(2000)
                    subprocess.call(
                        ["wmctrl", "-a", "interprete", "-b", "add,above"]
                    )
                    break
                except:
                    print("No se ha podido cargar el interprete virtual.")
        else:
            print("Blenderplayer ya se encuentra en ejecucion")

    def _show_glossary(self, codigo):
        """
        Navega a la pantalla del glosario y muestra la definición del concepto dado.
        """
        self.config.set_preference("definicion", codigo)
        self.states[-1].portada_glosario = False
        self.states[-1].limpiar_grupos()
        self.states[-1].ir_glosario()

    def load_text_content(self):
        # Load all user-facing text content from JSON.
        self.text_content = load_text_content()
        self.text_loader = TextLoader(self.text_content)

        # Inject glossary vocabulary into the palabra class so screens never
        # need to hard-code it.  The import is local to avoid a circular import
        # (palabra → pantalla → manejador).
        from librerias.palabra import palabra as Palabra
        glossary = self.text_content.get("glossary", {})
        Palabra.ENTRIES = glossary.get("entries", {})
        Palabra.DEFINITIONS = glossary.get("definitions", {})
        Palabra.INDICES = glossary.get("indices", [])
        Palabra.INTERCALATED = glossary.get("intercalated", [])
