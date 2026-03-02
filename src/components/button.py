#!/usr/bin/env python3

from pygame import Rect, Surface
from pygame.font import match_font, Font, SysFont
from pygame.image import load
from pygame.mouse import get_pos
from pygame.sprite import Group, OrderedUpdates, Sprite

from .texto import Text
from .object import GameObject
from .spritesheet import SpriteSheet

RED = (213, 0, 0)
TEXT_COLOR = (255, 255, 255)


class Button(GameObject):
    """Animated sprite button built from a horizontal frame strip, with tooltip support."""

    def __init__(
        self,
        x,
        y,
        id,
        tooltip,
        font_size,
        filename,
        frames,
        colorkey=None,
        loop=False,
        frame_speed=1,
    ):
        """
        Initialise the button sprite.

        @param x: X coordinate at which to draw the button.
        @type x: int
        @param y: Y coordinate at which to draw the button.
        @type y: int
        @param id: Unique identifier for this button instance.
        @type id: str
        @param tooltip: Tooltip text shown when the cursor hovers over the button; pass "none" to suppress.
        @type tooltip: str
        @param font_size: Font size used to render the tooltip text.
        @type font_size: int
        @param filename: Path to the sprite-sheet image.
        @type filename: str
        @param frames: Number of frames (columns) in the sprite sheet.
        @type frames: int
        @param colorkey: Colour treated as transparent; omit if not needed.
        @type colorkey: tuple
        @param loop: If True the animation loops; defaults to False.
        @type loop: bool
        @param frame_speed: Ticks per frame; 1 is the fastest.
        @type frame_speed: int
        """

        Sprite.__init__(self)
        self.x = x
        self.y = y
        self.id = id
        self.obj_type = "button"

        # Boolean states
        self.loop = loop
        self.stop = True
        self.sonar = True

        # Tooltip attributes
        my_font = SysFont("arial", font_size)
        self.tooltip = tooltip
        self.tooltip_sprite = Sprite()
        self.tooltip_sprite.image = my_font.render(
            self.tooltip, True, (0, 0, 0), (230, 230, 130)
        )
        self.tooltip_sprite.rect = Rect((0, 0, 0, 0))
        self.tooltip_group = Group()

        ss = SpriteSheet(filename)
        self.current_image = Surface((0, 0))
        (_, _, width, height) = ss.sheet.get_rect()
        self.rect = Rect(x, y, int(width / frames), height)
        rt = Rect(0, 0, int(width / frames), height)
        self.images = ss.load_strip(rt, frames, colorkey=colorkey)

        self.current_frame = 0
        self.frame_speed = frame_speed
        self.frame_delta = frame_speed
        if self.frame_speed == 1:
            self.current_image = self.images[0]

    def update(self, group):
        """
        Show or hide the tooltip based on cursor position.

        @param group: Sprite group to which the tooltip sprite is added or removed.
        @type group: pygame.sprite.Group
        """

        if self.detect_collision():
            if not self.tooltip == "none":
                group.add(self.tooltip_sprite)
        else:
            group.remove(self.tooltip_sprite)

    def play_animation(self):
        """Start playing the button animation."""

        self.stop = False

    def stop_animation(self):
        """Stop the button animation."""

        self.stop = True

    def replay_animation(self):
        """Restart a non-looping animation from the first frame."""

        self.stop = False
        self.current_frame = 0

    def next(self):
        """Advance the button animation by one tick, updating the displayed frame."""

        if self.current_frame >= len(self.images):
            if self.loop:
                self.current_frame = 0
            else:
                self.stop = True

        if not self.stop:
            self.current_image = self.images[self.current_frame]
            self.frame_delta -= 1
            if self.frame_delta == 0:
                self.current_frame += 1
                self.frame_delta = self.frame_speed

    def play_sound(self, canal):
        """
        Play the button's default sound if the cursor is over it.

        @param canal: Mixer channel used to play the sound.
        @type canal: pygame.mixer.Channel
        """

        if self.detect_collision() and canal.get_busy and self.sonar:
            self.sonar = False
            # canal.play(self.sonido)

    def detect_collision(self):
        """
        Test whether the cursor is currently over the button.

        @return: True if the cursor is over the button, False otherwise.
        @rtype: bool
        """

        if self.rect.collidepoint(get_pos()):
            self.play_animation()
            if get_pos()[0] >= (1024 - self.tooltip_sprite.image.get_width()):
                x = 1024 - self.tooltip_sprite.image.get_width() - 10
                # The tooltip text is always rendered with a small offset
                # hence the +10 and +20 values
                self.tooltip_sprite.rect = (x + 10, get_pos()[1] + 20, 0, 0)
            else:
                self.tooltip_sprite.rect = (get_pos()[0] + 10, get_pos()[1] + 20, 0, 0)
            return True
        else:
            self.sonar = True
            self.tooltip_group.empty()
            self.stop_animation()
            self.current_frame = 0
            self.current_image = self.images[0]
            self.stop = True
            return False

    def get_reader_text(self):
        """Text spoken by the screen reader when this button is focused."""
        return self.tooltip


class TextButton(GameObject):
    """Text-labelled button with an optional background image."""

    def __init__(self, identificador, parent, text, background=0, width=500):
        """
        Initialise the text button.

        @param identificador: Unique identifier for this button.
        @type identificador: str
        @param parent: Screen manager instance.
        @type parent: Manejador
        @param text: Label text displayed on the button.
        @type text: str
        @param background: Background style; 0 for image background, 1 for plain text surface.
        @type background: int
        @param width: Button width in pixels, used to centre the text.
        @type width: int
        """

        Sprite.__init__(self)
        self.width = width
        self.parent = parent
        tipografia = match_font("FreeSans", False, False)
        font = Font(tipografia, parent.config.get_font_size())
        self.identificador = identificador
        misc_path = "../imagenes/png/varios/"

        if background == 0:
            texto1 = font.render(text, 1, TEXT_COLOR)
            textorect = texto1.get_rect()
            texto2 = font.render(text, 1, RED)
            self.img_bg = load(misc_path + "img-boton.png")
            self.img_bg2 = load(misc_path + "img-boton.png")
            imgrect = self.img_bg.get_rect()
            textorect.center = (
                imgrect.center[0],
                imgrect.center[1] + imgrect.center[1] / 3,
            )
            self.img_bg.blit(texto1, textorect)
            self.img_bg2.blit(texto2, textorect)
            self.rect = self.img_bg.get_rect()
            self.image = self.img_bg

        if background == 1:
            txt = Text(0, 0, text, parent.config.get_font_size(), "active_text", self.width)
            self.rect = Rect(0, 0, self.width, txt.final_width)
            image_texto = Surface((self.width, txt.final_width))
            image_texto.fill((255, 255, 255))
            image_texto.set_colorkey((255, 255, 255))
            for i in txt.words:
                image_texto.blit(i.image, i.rect)
            self.image = image_texto
            self.img_bg = image_texto
            self.img_bg2 = image_texto

    def set_hover_state(self, status):
        """Toggle the button between its two background images."""

        if status:
            self.image = self.img_bg2
        else:
            self.image = self.img_bg


class RenderButton(OrderedUpdates):
    """Ordered sprite group that advances each Button member's frame on every draw call."""

    def draw(self, surface):
        """
        Draw all member buttons and advance their frames.

        @param surface: Surface to draw onto.
        @type surface: pygame.Surface
        """

        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sprites:
            self.spritedict[spr] = surface_blit(spr.current_image, spr.rect)
            spr.next()
