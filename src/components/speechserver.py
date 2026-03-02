#!/usr/bin/env python
"""Stub TTS interface intended to wrap a speech-dispatcher back-end (currently disabled)."""

# import speechd
import subprocess

from manejador import Manager as parent


class Speechserver:
    """Stub interface for the eSpeak / speech-dispatcher TTS back-end (all calls are currently no-ops)."""

    def __init__(self):
        """Initialise the speech server (no-op; back-end is disabled)."""
        # self.parent = parent
        # self.dic_vel = {"baja": 0, "media": 25, "rapida": 50}
        # self.speaker = speechd.Speaker('SERVERSPEECH')
        # self.speaker.set_punctuation(speechd.PunctuationMode.NONE)
        # self.speaker.set_language("es")
        # self.update_server()
        # self.hablando = False
        # self.ultima_lectura = ""
        pass

    def update_server(self):
        """Sync the TTS speech rate from user configuration (no-op; back-end is disabled)."""
        # self.speaker.set_rate(self.dic_vel[self.parent.config.synvel])
        pass

    def processtext2(self, texto, lector_activo):
        """
        Send text to the TTS engine, allowing requests to queue (no-op; back-end is disabled).

        @param texto: Text to be spoken.
        @type texto: str
        @param lector_activo: True if the screen reader is enabled.
        @type lector_activo: bool
        """
        # if lector_activo:
        #     self.data = texto
        #     self.speaker.speak(self.data)

    def processtext(self, texto, lector_activo, continuar=True):
        """
        Send text to the TTS engine, interrupting any ongoing speech (no-op; back-end is disabled).

        @param texto: Text to be spoken.
        @type texto: str
        @param lector_activo: True if the screen reader is enabled.
        @type lector_activo: bool
        @param continuar: Reserved for future queue-control behaviour.
        @type continuar: bool
        """
        # self.ultima_lectura = texto
        # if lector_activo:
        #     if self.hablando and continuar:
        #         self.stopserver()
        #     self.data = texto
        #     self.speaker.speak(self.data)
        #     self.hablando = True
        pass

    def stopserver(self):
        """Stop the TTS engine's current utterance (no-op; back-end is disabled)."""
        # self.speaker.stop()
        # self.hablando = False
        pass

    def repetir(self):
        """Repeat the last spoken text (no-op; back-end is disabled)."""
        # self.stopserver()
        # self.speaker.speak(self.data)
        pass

    def quitserver(self):
        """Close the TTS connection and stop the speech-dispatcher process (no-op; back-end is disabled)."""
        # self.speaker.close()
        # subprocess.call(['pkill', '-9', 'speech-dispatcher'])
        pass
