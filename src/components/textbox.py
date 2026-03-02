#!/usr/bin/env python

import pygame

from .words import Word


class TextBox(pygame.sprite.Sprite):
    """Text-input box that manages keyboard input and horizontal scrolling as the box fills."""

    def __init__(self, x, y, expected_answer, screen, size="high"):
        """
        Initialise the text input box.

        @param x: X coordinate of the box.
        @type x: int
        @param y: Y coordinate of the box.
        @type y: int
        @param expected_answer: Expected answer string used for comparison.
        @type expected_answer: str
        @param screen: Surface on which the box is displayed.
        @type screen: pygame.Surface
        @param size: Size preset for the box: "low", "medium", or "high".
        @type size: str
        """
        self.eventlist = [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            0,
            "q",
            "w",
            "e",
            "r",
            "t",
            "y",
            "u",
            "i",
            "o",
            "p",
            "a",
            "s",
            "d",
            "f",
            "g",
            "h",
            "j",
            "k",
            "l",
            "z",
            "x",
            "c",
            "v",
            "b",
            "n",
            "m",
        ]
        self.time = pygame.time.Clock()
        self.time.tick(30)
        self.x = 0
        self.cursor_char = " "
        self.keyboard_active = False
        self.screen = screen
        self.screen_center = screen.get_rect().center
        self.active = True
        self.rect = pygame.rect
        self.height = 0
        if size == "high":
            img = pygame.image.load("../imagenes/png/varios/cuadro-texto.png")
            self.width = img.get_rect().width
            self.rect = img.get_rect()
        if size == "medium":
            img = pygame.image.load("../imagenes/png/varios/cuadro-texto.png")
            self.width = img.get_rect().width
            self.rect = img.get_rect()
        if size == "low":
            img = pygame.image.load("../imagenes/png/varios/cuadro-texto.png")
            self.width = img.get_rect().width
            self.rect = img.get_rect()
        self.rect.move_ip(x, y)
        self.chars = []
        self.text = str
        self.clock = pygame.time.Clock()
        self.text_sprite = pygame.sprite.Sprite()
        self.width = self.rect.width
        self.expected_answer = expected_answer
        self.button = pygame.sprite.Sprite()
        self.button.rect = (self.rect.left + 80, 0, 60, 30)

    def process_key(self, key_input):
        """
        Append or remove a character based on the key code received.

        @param key_input: Key code or control string ("+1" for space, "-1" for backspace, or a pygame key integer).
        @type key_input: int or str
        """
        if key_input == "+1":
            self.chars.append(" ")
        elif key_input == "-1":
            if len(self.chars) >= 1:
                self.chars.pop()
        elif key_input == 48:
            self.chars.append("0")
        elif key_input == 49:
            self.chars.append("1")
        elif key_input == 50:
            self.chars.append("2")
        elif key_input == 51:
            self.chars.append("3")
        elif key_input == 52:
            self.chars.append("4")
        elif key_input == 53:
            self.chars.append("5")
        elif key_input == 54:
            self.chars.append("6")
        elif key_input == 55:
            self.chars.append("7")
        elif key_input == 56:
            self.chars.append("8")
        elif key_input == 57:
            self.chars.append("9")

    def render(self):
        """Render the current input text into the box sprite, scrolling if the text overflows."""
        chars_str = ""
        for i in self.chars:
            chars_str += i
        self.text = chars_str
        chars_str += self.cursor_char
        x = Word(chars_str, 20, "textbox")
        self.text_sprite.image = x.get_text()
        self.text_sprite.image.set_colorkey((255, 255, 255))
        self.text_sprite.rect = self.text_sprite.image.get_rect()
        rect = (
            self.text_sprite.rect.width - self.width,
            0,
            self.width,
            self.text_sprite.rect.height,
        )
        if self.text_sprite.rect.width > self.width:
            self.text_sprite.image = self.text_sprite.image.subsurface(rect)
        self.text_sprite.rect = x.get_rect()
        self.text_sprite.rect.top = self.rect.top
        self.text_sprite.rect.left = self.rect.left

    def handle_event(self, event):
        """
        Handle a single keyboard event for the text box.

        @param event: Event to process.
        @type event: pygame.event.Event
        @return: True if the Enter key was pressed, None otherwise.
        @rtype: bool or None
        """
        if event.type == pygame.K_ESCAPE:
            self.active = False
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.process_key("-1")
            elif event.key == pygame.K_SPACE:
                self.process_key("+1")
            elif event.key == pygame.K_RETURN:
                return True
            else:
                self.process_key(event.key)
        self.render()

    def blink_cursor(self):
        """Blink the cursor character '|' in the text box every 600 milliseconds."""
        if self.keyboard_active:
            self.x += self.time.get_time()
            if self.x in range(0, 400):
                self.cursor_char = "|"
            else:
                self.cursor_char = " "
            if self.x > 600:
                self.x = 0
            self.render()
        else:
            self.cursor_char = " "
            self.render()

    def process(self, event, keyboard_active):
        """
        Process a keyboard event when the box is active.

        @param event: Event to evaluate.
        @type event: pygame.event.Event
        @param keyboard_active: True if the box is currently accepting keyboard input.
        @type keyboard_active: bool
        @return: True if the Enter key was pressed, None otherwise.
        @rtype: bool or None
        """
        self.keyboard_active = keyboard_active
        if keyboard_active:
            if self.handle_event(event):
                return True

    def reset(self):
        self.chars = []
        self.text = ""

    def check_answer(self):
        if self.expected_answer.lower() == self.text:
            return True
        else:
            return False

    def has_min_length(self):
        """
        Check whether the current input has at least two characters.

        @return: True if the input contains two or more characters, False otherwise.
        @rtype: bool
        """
        if len(self.chars) >= 2:
            return True
        else:
            return False

    def is_empty(self):
        """
        Check whether the text box is empty.

        @return: True if the input is empty, False otherwise.
        @rtype: bool
        """
        if len(self.chars) < 1:
            return True
        else:
            return False

    def get_text(self):
        """
        Return the text currently entered in the box.

        @return: The entered text.
        @rtype: str
        """
        return self.text

    def add_to_group(self, grupo):
        grupo.add(self.text_sprite)

    def set_x(self, x):
        """
        Set the X position of the text box.

        @param x: New X coordinate.
        @type x: int
        """
        self.x = x

    def set_y(self, y):
        """
        Set the Y position of the text box.

        @param y: New Y coordinate.
        @type y: int
        """
        self.y = y
