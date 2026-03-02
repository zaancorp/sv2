#!/usr/bin/env python
"""Glossary screen allowing students to look up plant biology concepts (screen 10)."""

import pygame

from components import screen
from components.texto import Text
from components.image import Image

from paginas import pantalla2


banners = [
    "banner-inf",
    "banner-glo",
]

buttons = ["home", "back"]


class Screen(screen.Screen):
    """Screen that presents a navigable alphabetical glossary of plant biology terms."""

    def __init__(self, parent):
        """
        Initialise the glossary screen and display the entry for the last-viewed concept.

        @param parent: Screen manager instance.
        @type parent: Manejador
        """

        self.name = "screen_10"
        super().__init__(parent, self.name)

        self.is_overlay = False

        self.caja_concepto = Image(590, 190, self.misc_path + "caja-concepto.png")

        self.load_banners(banners)
        self.load_texts()
        self.load_buttons(buttons)

        inicial = self.parent.config.get_preference("definicion", "")[0].upper()
        self.abc.indexar(inicial)
        self.word_group.add(
            self.abc.words,
            self.indices(inicial, self.parent.config.get_preference("definicion", "")),
            self.mostrar_concepto(self.parent.config.get_preference("definicion", "")),
        )
        self.caja_concepto.resize(height=self.concepto.total_height)
        self.word_group.add(self.abc.words)
        self.banner_group.add(self.banner_glo, self.caja_concepto, self.banner_inf)
        self.button_group.add(self.back, self.home)

    def load_texts(self):
        """Build the alphabet index, concept display, and all glossary entry text objects."""
        self.abc = Text(
            290,
            140,
            "A  B  C  D  E  F  G  H  I  J  K  L  M  N  Ñ  O  P  Q  R  S  T  U  V  W  X  Y  Z ",
            18,
            "indice",
            1010,
        )
        self.concepto = Text(
            600, 200, "", self.parent.config.get_font_size(), "concepto", 1000
        )
        self.a_absorber = Text(330, 200, "Absorber ", 22, "definicion", 900)
        self.c_celula = Text(330, 200, "Célula ", 22, "definicion", 900)
        self.c_componentes = Text(330, 250, "Componentes ", 22, "definicion", 900)
        self.f_fotosintesis = Text(330, 200, "Fotosíntesis ", 22, "definicion", 900)
        self.g_germinacion = Text(330, 200, "Germinación ", 22, "definicion", 900)
        self.g_germinar = Text(330, 250, "Germinar ", 22, "definicion", 900)
        self.m_minerales = Text(330, 200, "Mineral ", 22, "definicion", 900)
        self.n_nutrientes = Text(330, 200, "Nutriente ", 22, "definicion", 900)
        self.o_organo = Text(330, 200, "Órgano ", 22, "definicion", 900)
        self.a_asexual = Text(330, 200, "Reproducción asexual ", 22, "definicion", 900)
        self.s_sexual = Text(330, 250, "Reproducción sexual ", 22, "definicion", 900)
        self.t_transformacion = Text(330, 200, "Transformación ", 22, "definicion", 900)
        self.t_transporte = Text(330, 250, "Transportar ", 22, "definicion", 900)

    def handleEvents(self, events):
        """
        Process input events for this screen.

        @param events: Event list from the main loop.
        @type events: list
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.parent.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.clear_groups()
                    self.parent.changeState(pantalla2.Screen(self.parent))

            if pygame.sprite.spritecollideany(self.mouse, self.word_group):
                sprite = pygame.sprite.spritecollide(
                    self.mouse, self.word_group, False
                )
                if pygame.mouse.get_pressed() == (True, False, False):
                    if sprite[0].definable == True:
                        self.abc.indexar(sprite[0].text)
                        self.word_group.update(1)
                        sprite[0].selected = True
                        sprite[0].highlight()
                        self.word_group.empty()
                        self.banner_group.remove(self.caja_concepto)
                        self.word_group.add(
                            self.abc.words, self.indices(sprite[0].text)
                        )
                    if sprite[0].definition == True:
                        self.word_group.update(2)
                        sprite[0].selected = True
                        self.banner_group.add(self.caja_concepto)
                        self.word_group.remove(self.concepto.words)
                        self.word_group.add(self.mostrar_concepto(sprite[0].code))
                        self.caja_concepto.resize(height=self.concepto.total_height)

            if pygame.sprite.spritecollideany(self.mouse, self.button_group):
                sprite = pygame.sprite.spritecollide(
                    self.mouse, self.button_group, False
                )
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if sprite[0].id == "home":
                        self.clear_groups()
                        self.parent.changeState(pantalla2.Screen(self.parent))
                    elif sprite[0].id == "back":
                        self.clear_groups()
                        self.parent.popState()
        self.handle_magnifier(events)

    def update(self):
        """Update cursor position, magnifier, and button tooltips."""
        self.mouse.update()
        self.magnifier.magnificar(self.parent.screen)
        self.button_group.update(self.tooltip_group)

    def mostrar_concepto(self, palabra):
        """
        Build a Text object for the given glossary term and return its word sprites.

        @param palabra: Glossary term key used to look up the concept text.
        @type palabra: str
        @return: Word sprites for the concept definition.
        @rtype: list
        """

        self.concepto = Text(
            600,
            200,
            self.parent.text_loader.concept(palabra),
            self.parent.config.get_font_size(),
            "concepto",
            1000,
        )
        return self.concepto.words

    def indices(self, valor, palabra_negrita=""):
        """
        Return the list of glossary entry word-sprite groups for the given letter, marking one entry as selected.

        @param valor: Uppercase letter used to select the index bucket.
        @type valor: str
        @param palabra_negrita: Term code that should be rendered as selected (bold); empty string for none.
        @type palabra_negrita: str
        @return: Word sprite lists for each matching glossary entry.
        @rtype: list
        """
        indices = {
            "A": (self.a_absorber,),
            "C": (self.c_celula, self.c_componentes),
            "F": (self.f_fotosintesis,),
            "G": (self.g_germinacion, self.g_germinar),
            "M": (self.m_minerales,),
            "N": (self.n_nutrientes,),
            "O": (self.o_organo,),
            "R": (self.a_asexual, self.s_sexual),
            "T": (self.t_transformacion, self.t_transporte),
        }
        palabras = []
        if valor in indices:
            tupla = indices[valor]
            for i in tupla:
                if i.words[0].code == palabra_negrita:
                    i.words[0].selected = True
                else:
                    i.words[0].selected = False
                    i.words[0].update(2)
                palabras.append(i.words)
            return palabras
