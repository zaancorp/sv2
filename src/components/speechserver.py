#!/usr/bin/env python
"""TTS interface dispatching to the best available system speech engine.

On macOS the built-in ``say`` command is used.  On Linux ``espeak-ng`` is
preferred, with a fallback to ``espeak``.  If no engine is found all calls
are silent no-ops so the rest of the application keeps working.
"""

import platform
import shutil
import subprocess


class Speechserver:
    """TTS interface that dispatches to the best available system speech engine.

    Speech is launched in a background subprocess so it never blocks the game
    loop.  ``processtext`` interrupts any ongoing speech before speaking;
    ``processtext2`` only speaks if the engine is currently idle.
    """

    # Maps the user-configured speed tier to words-per-minute strings accepted
    # by both ``say`` (macOS) and ``espeak``/``espeak-ng`` (Linux).
    _WPM = {"baja": "80", "media": "150", "rapida": "220"}

    def __init__(self):
        """Detect the available TTS engine and initialise playback state."""
        self._proc = None         # running speech subprocess, if any
        self._last_text = ""      # most recently requested text (for repetir())
        self._rate_key = "media"  # default speed tier
        self._engine = self._detect_engine()

    def _detect_engine(self):
        """Return the name of the first usable TTS command, or None.

        @return: Command name (e.g. ``"say"``, ``"espeak-ng"``), or None if
            no engine is available.
        @rtype: str | None
        """
        if platform.system() == "Darwin":
            return "say"
        for cmd in ("espeak-ng", "espeak"):
            if shutil.which(cmd):
                return cmd
        return None

    def _stop_proc(self):
        """Terminate the current speech subprocess if it is still running."""
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
            self._proc = None

    def _speak(self, text):
        """
        Launch a background TTS subprocess for *text* at the current rate.

        @param text: Text to be spoken.
        @type text: str
        """
        if not self._engine:
            return
        wpm = self._WPM.get(self._rate_key, "150")
        if self._engine == "say":
            self._proc = subprocess.Popen(["say", "-r", wpm, text])
        else:
            # espeak / espeak-ng: -v selects voice/language, -s sets speed.
            self._proc = subprocess.Popen(
                [self._engine, "-v", "es", "-s", wpm, text]
            )

    def update_server(self, rate_key=None):
        """
        Update the speech rate.

        Pass one of ``"baja"``, ``"media"``, or ``"rapida"``; omit to keep
        the current rate.  The new rate takes effect on the next ``processtext``
        or ``repetir`` call.

        @param rate_key: Speed tier to apply; unchanged if None.
        @type rate_key: str | None
        """
        if rate_key is not None:
            self._rate_key = rate_key

    def processtext(self, texto, lector_activo, continuar=True):
        """
        Speak *texto*, interrupting any ongoing speech.

        @param texto: Text to be spoken.
        @type texto: str
        @param lector_activo: True if the screen reader is enabled.
        @type lector_activo: bool
        @param continuar: If True (default), stop current speech before
            starting the new utterance.
        @type continuar: bool
        """
        if not lector_activo:
            return
        self._last_text = texto
        if continuar:
            self._stop_proc()
        self._speak(texto)

    def processtext2(self, texto, lector_activo):
        """
        Speak *texto* only if no speech is currently playing.

        @param texto: Text to be spoken.
        @type texto: str
        @param lector_activo: True if the screen reader is enabled.
        @type lector_activo: bool
        """
        if not lector_activo:
            return
        self._last_text = texto
        if not self._proc or self._proc.poll() is not None:
            self._speak(texto)

    def stopserver(self):
        """Stop the current TTS utterance."""
        self._stop_proc()

    def repetir(self):
        """Repeat the last spoken text from the beginning."""
        if self._last_text:
            self._stop_proc()
            self._speak(self._last_text)

    def quitserver(self):
        """Terminate the TTS process and release resources."""
        self._stop_proc()
