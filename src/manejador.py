#!/usr/bin/env python

import gc
import sys
import pygame
import subprocess

from components.singleton import Singleton
from components.magnifier import Rendermag
from components.configuration import Configuration
from components.text_repository import (
    load_text_content as _load_text_content,
    invalidate_text_cache,
    content_path_for_language,
)
from components.text_loader import TextLoader


class Manager(metaclass=Singleton):
    """Screen-state machine that owns the display surface and drives the main loop."""

    magnifier_active = False
    DRAW_DEBUG_RECTANGLES = False
    RETURN_TO_PREV_SCREEN = False
    config = Configuration()
    magnifier_group = Rendermag()
    interpreter_paths = [
        "/opt/blender/blenderplayer",
        "blenderplayer",
        "/usr/bin/blenderplayer",
    ]

    def __init__(self, titulo, size=(1024, 572), fullscreen=False):
        """
        Initialise pygame, the display window, and text content.

        @param titulo: Window caption.
        @type titulo: str
        @param size: Window resolution in pixels.
        @type size: tuple
        @param fullscreen: True to display in fullscreen mode; False for a window.
        @type fullscreen: bool
        """
        pygame.init()
        self.first_run = True
        self.animation_index = 0
        self.states = []
        self.running = True
        self.screen = pygame.display.set_mode(size)
        self.load_text_content()
        pygame.display.set_caption(titulo)
        icon = pygame.image.load("./iconos/sembrando96x96.png")
        pygame.display.set_icon(icon)

    def cleanUp(self):
        """Stop TTS, clean up all loaded screens, kill any running Blenderplayer process, and exit."""
        self.states[-1].speech_server.stopserver()
        self.states[-1].speech_server.quitserver()
        while len(self.states) > 0:
            state = self.states.pop()
            state.cleanUp()
        if not subprocess.call(["pgrep", "blenderplayer"]):
            subprocess.call(["pkill", "-9", "blenderplayer"])
        print("Cerrando servidor de texto a voz")
        sys.exit(0)

    def changeState(self, gameState):
        """
        Replace the current screen with a new one.

        @param gameState: Screen instance to load.
        @type gameState: Screen
        """
        if len(self.states) > 0:
            state = self.states.pop()
            state.cleanUp()
        self.states.append(gameState)
        self.states[-1].start()
        gc.collect()

    def pushState(self, gameState):
        """
        Overlay a new screen on top of the current one without cleaning it up.

        @param gameState: Screen instance to push.
        @type gameState: Screen
        """
        if len(self.states) > 0:
            self.states[-1].pause()
        self.states.append(gameState)
        self.states[-1].start()

    def popState(self):
        """Remove and clean up the top screen, then resume the previous one."""
        if len(self.states) > 0:
            state = self.states.pop()
            state.cleanUp()
        if len(self.states) > 0:
            self.states[-1].resume()

    def handleEvents(self, events):
        """
        Delegate event processing to the active screen.

        @param events: Event list from the main loop.
        @type events: list
        """
        self.states[-1].handleEvents(events)

    def update(self):
        """Delegate update logic to the active screen."""
        self.states[-1].update()

    def draw(self):
        """Delegate drawing to the active screen, flip the display, and cap the frame rate at 30 fps."""
        self.states[-1].draw()
        self.states[-1].frame_clock.tick(30)
        pygame.display.flip()

    def quit(self):
        """Signal the main loop to stop."""
        self.running = False

    def show_concept(self, codigo):
        """
        Dispatch a concept code to the virtual sign-language interpreter or the glossary screen.

        Launches Blenderplayer when auditory accessibility is enabled; otherwise navigates to
        the glossary.

        @param codigo: Vocabulary key identifying the concept to display.
        @type codigo: str
        """
        if self.config.get_preference("disc_audi", False):
            self._launch_interpreter(codigo)
        else:
            self._show_glossary(codigo)

    def _launch_interpreter(self, codigo):
        """
        Launch the Blenderplayer subprocess to animate the given concept.

        Does nothing if Blenderplayer is already running.

        @param codigo: Vocabulary key to pass to the interpreter.
        @type codigo: str
        """
        running = subprocess.call(["pgrep", "blenderplayer"])
        if running == 1:
            color = self.config.get_preference("color", 0)
            genero = self.config.get_preference("genero", "Hombre")
            velocidad = self.config.get_preference("velocidad", 0.5)
            for ruta in self.interpreter_paths:
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
        Navigate the active screen to the glossary and display the given concept's definition.

        @param codigo: Vocabulary key identifying the concept to look up.
        @type codigo: str
        """
        self.config.set_preference("definicion", codigo)
        self.states[-1].at_glossary_cover = False
        self.states[-1].clear_groups()
        self.states[-1].go_to_glossary()

    def load_text_content(self):
        """Load all user-facing text from the active language's JSON file and populate the glossary on the Word class."""
        # Load all user-facing text content from the language-specific JSON.
        lang = self.config.get_language()
        path = content_path_for_language(lang)
        self.text_content = _load_text_content(path)
        self.text_loader = TextLoader(self.text_content)

        # Inject glossary vocabulary into the Word class so screens never
        # need to hard-code it.  The import is local to avoid a circular import
        # (Word/palabra → pantalla → manejador).
        from components.words import Word
        glossary = self.text_content.get("glossary", {})
        Word.ENTRIES   = glossary.get("entries", {})
        Word.DEFINITIONS = glossary.get("definitions", {})
        Word.INDICES     = glossary.get("indices", [])
        Word.INTERCALATED = glossary.get("intercalated", [])

    def reload_text_content(self):
        """Invalidate the LRU cache and reload text for the active language."""
        invalidate_text_cache()
        self.load_text_content()
