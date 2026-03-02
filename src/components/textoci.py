#!/usr/bin/env python
"""Text layout class that supports inline image substitution within a word sequence."""

from .words import Word


class InlineText:
    """Word-wrapped text layout that can substitute word tokens with inline images."""

    def __init__(self, x, y, text, size, text_type, right_limit, dic=0):
        """
        Lay out the text as a sequence of Word sprites, optionally replacing words with images.

        @param x: Left starting position in pixels.
        @type x: int
        @param y: Top starting position in pixels.
        @type y: int
        @param text: Full text string to lay out.
        @type text: str
        @param size: Font size in points.
        @type size: int
        @param text_type: TextType int value passed to each Word.
        @type text_type: int
        @param right_limit: Right boundary in pixels; words that exceed it wrap to the next line.
        @type right_limit: int
        @param dic: Mapping of word tokens to replacement pygame.Surface objects; 0 means no substitutions.
        @type dic: dict | int
        """
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.text_type = text_type
        self.words = []
        self.text = text
        self.buffer = ""
        self.word_gap = 6
        self.line_number = 0
        self.final_width = 0
        self.dic = dic

        for i in self.text:
            self.buffer += i
            if i == " ":
                if (
                    self.buffer == "Reproducción " and self.text_type != "active_text"
                ) or (
                    self.buffer == "reproducción " and self.text_type != "active_text"
                ):
                    pass
                else:
                    self.words.append(
                        Word(self.buffer.strip(" "), size, self.text_type)
                    )
                    self.buffer = ""

        self.left_limit = x
        self.right_limit = right_limit
        #        medidas, width, line_height = self.calcular(self.start_x)
        medidas, width, line_height = self.compute_layout(self.start_x)
        self.final_width = width
        self.word_gap = 6 + medidas[self.line_number]

        for i in self.words:
            if (self.start_x + i.rect.width > self.right_limit) or (i.text == "|"):
                self.line_number += 1
                self.word_gap = 6 + medidas[self.line_number]
                self.start_x = self.left_limit
                #                y += line_height[self.line_number-1]
                y += line_height
            i.rect.left = self.start_x
            #            i.rect.y = y + line_height[self.line_number]/2 - i.rect.h/2
            i.rect.y = y + line_height / 2 - i.rect.h / 2

            if not self.dic == 0:
                for n in self.dic.keys():
                    if n == i.text:
                        i.image = self.dic[n]
                        i.rect.width, i.rect.height = i.image.get_size()
                        i.rect.x = self.start_x
                        i.rect.y = y
            self.start_x += i.rect.width + self.word_gap

    def calcular(self, x):
        """
        Compute per-line justification spacing and total text height (variable line heights).

        @param x: Starting X position used to measure line widths.
        @type x: int
        @return: Tuple of (per-line spacing list, total height, per-line heights list).
        @rtype: tuple
        """
        px = self.start_x
        nro_lineas = 0
        medida_lineas = []
        ppl = 0
        width = 0
        ancho_total = 0
        altos_lineas = []
        for i in self.words:
            if (px + i.rect.width > self.right_limit) or (i.text == "|"):
                if ppl == 1:
                    medida_lineas.append((self.right_limit - px) / ppl)
                else:
                    medida_lineas.append((self.right_limit - px) / (ppl - 1.0))
                ppl = 0
                px = self.left_limit
                nro_lineas += 1
                altos_lineas.append(width)
                width = 0
            if not self.dic == 0:
                for n in self.dic.keys():
                    if n == i.text:
                        i.image = self.dic[n]
                        i.rect = i.image.get_rect()

            px += i.rect.width + self.word_gap
            if i.rect.h > width:
                width = i.rect.height
            ppl += 1
        medida_lineas.append(0)
        altos_lineas.append(width)
        for i in altos_lineas:
            ancho_total += i
        return medida_lineas, ancho_total, altos_lineas

    def compute_layout(self, x):
        """
        Compute per-line justification spacing and total text height using a uniform line height.

        @param x: Starting X position used to measure line widths.
        @type x: int
        @return: Tuple of (per-line spacing list, total height, uniform line height).
        @rtype: tuple
        """
        px = self.start_x
        nro_lineas = 0
        medida_lineas = []
        ppl = 0
        height = 0
        width = 0
        ancho_total = 0
        altos_lineas = []
        for i in self.words:
            if not self.dic == 0:
                for n in self.dic.keys():
                    if n == i.text:
                        i.image = self.dic[n]
                        i.rect = i.image.get_rect()

            if px + i.rect.width > self.right_limit:
                if ppl == 1:
                    medida_lineas.append((self.right_limit - px) / ppl)
                else:
                    medida_lineas.append((self.right_limit - px) / (ppl - 1.0))
                ppl = 0
                px = self.left_limit
                nro_lineas += 1
                altos_lineas.append(width)
                width = 0

            #            if not self.dic == 0 :
            #                for n in self.dic.keys():
            #                    if n == i.text:
            #                        i.image = self.dic[n]
            #                        i.rect = i.image.get_rect()

            px += i.rect.width + self.word_gap
            if i.rect.h > width:
                width = i.rect.height
            ppl += 1

        medida_lineas.append(0)
        altos_lineas.append(width)
        for i in altos_lineas:
            if i > height:
                height = i
        ancho_total = height * (nro_lineas + 1)
        return medida_lineas, ancho_total, height
