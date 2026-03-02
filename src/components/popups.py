#!/usr/bin/env python3
"""Modal popup sprites for the sv2 screen system."""

from pygame import Rect, Surface

from pygame.image import load
from pygame.key import get_pressed
from pygame.mouse import get_pos
from pygame.sprite import Sprite

from pygame import MOUSEBUTTONDOWN, K_RETURN

from .texto import Text
from .textoci import InlineText
from .background import Background
from .button import TextButton


class PopUp(Sprite):
    """Modal popup sprite supporting three layout types: image+button (0), list menu (1), and inline image (2)."""

    def __init__(
        self,
        parent,
        texto1,
        btn_label,
        images,
        group,
        layout_type=0,
        px=512,
        py=281,
        extra_width=0,
    ):
        """
        Build and render the popup surface.

        @param parent: Screen manager instance.
        @type parent: Manejador
        @param texto1: Text to display; a plain string for layout_type 0 and 2, a list of strings for layout_type 1.
        @type texto1: str | list
        @param btn_label: Label for the dismiss button (used only when layout_type == 0).
        @type btn_label: str
        @param images: Image(s) to display. For layout_type 0: a Surface or a (side_image, bottom_image) tuple.
            For layout_type 2: a dict mapping word tokens to replacement Surface objects. Unused for layout_type 1.
        @type images: pygame.Surface | tuple | dict
        @param group: Sprite group to which the popup sprite is added when shown.
        @type group: pygame.sprite.Group
        @param layout_type: Layout type: 0 = text + side image + button, 1 = text + button list, 2 = inline images.
        @type layout_type: int
        @param px: Horizontal centre of the popup in screen coordinates.
        @type px: int
        @param py: Vertical centre of the popup in screen coordinates.
        @type py: int
        @param extra_width: Extra width added to the base popup surface.
        @type extra_width: int
        """
        Sprite.__init__(self)
        self.parent = parent
        self.sprite = Sprite()
        misc_path = "./images/png/varios/"
        self.text_content = Surface
        self.layout_type = layout_type
        self.arreglo_botones = []
        self.group = group
        self.click = -1
        self.activo = 0
        self.extra_width = 0

        if layout_type == 0:
            self.img_bg = load(misc_path + "cuadropop-up.png").convert_alpha()
            self.sprite.image = load(misc_path + "cuadropop-up.png").convert_alpha()
            self.sprite.rect = self.sprite.image.get_rect()
            x = 30
            y = 30
            self.text_content = Text(
                x,
                y,
                texto1[0],
                parent.config.get_font_size(),
                "active_text",
                (self.sprite.rect.width * 2 / 3),
            )
            self.text_area = Rect(
                x, y, self.sprite.rect.w * 2 / 3, self.text_content.total_height
            )
            self.images_area = Rect(
                (self.sprite.rect.w * 2 / 3) + 80,
                y,
                self.sprite.rect.w / 3,
                self.text_content.total_height,
            )
            self.parent = parent
            self.action_btn = TextButton(0, self.parent, btn_label)
            self.action_btn.relocate(
                self.sprite.rect.width / 2,
                self.text_area.h + x * 2 + self.action_btn.rect.h / 2,
            )
            self.btn_rect = Rect(
                self.action_btn.rect.x,
                self.action_btn.rect.y,
                self.action_btn.rect.width,
                self.action_btn.rect.height,
            )
            self.sprite.image = Background(
                self.sprite.rect.w, self.action_btn.rect.y + self.action_btn.rect.h + x, 5
            ).return_imagen()
            self.side_image = Sprite()

            if type(images) != Surface:
                self.side_image2 = Sprite()
                self.side_image.image = images[0]
                self.side_image.rect = self.side_image.image.get_rect()
                self.side_image.rect.center = (
                    self.sprite.rect.w * 2 / 3 + (self.sprite.rect.w / 3) / 2,
                    self.images_area.h / 2 + self.btn_rect.h / 2,
                )
                self.side_image2.image = images[1]
                self.side_image2.rect = self.side_image.image.get_rect()
                self.side_image2.rect.left = x
                self.side_image2.rect.y = self.text_area.h + 40
                self.sprite.image.blit(self.side_image2.image, self.side_image2.rect)

            else:
                self.side_image.image = images
                self.side_image.rect = self.side_image.image.get_rect()
                self.side_image.rect.center = (
                    self.sprite.rect.w * 2 / 3 + (self.sprite.rect.w / 3) / 2,
                    self.images_area.h / 2 + self.btn_rect.h / 2,
                )
            if self.side_image.rect.y < 5:
                self.side_image.rect.y = 6
            for i in self.text_content.words:
                self.sprite.image.blit(i.image, i.rect)
            self.sprite.image.blit(self.action_btn.image, self.action_btn.rect)
            self.sprite.image.blit(self.side_image.image, self.side_image.rect)
            self.sprite.rect.center = (px, py)
            self.btn_rect.center = (
                self.sprite.rect.x + self.sprite.rect.width / 2,
                self.sprite.rect.y + self.text_area.h + x * 2 + self.action_btn.rect.h / 2,
            )

        if layout_type == 1:
            self.img_bg = load(misc_path + "cuadropop-up.png").convert_alpha()
            self.sprite.image = load(misc_path + "cuadropop-up.png").convert_alpha()
            self.sprite.rect = self.sprite.image.get_rect()
            x = 15
            y = 15
            o = 0
            spacing = 30
            tabulacion = 30
            self.sprite.rect.w += extra_width
            for i in texto1:
                if o == 0:
                    self.text_content = Text(
                        x,
                        y,
                        i,
                        parent.config.get_font_size(),
                        "active_text",
                        (self.sprite.rect.width) - x,
                    )
                if o > 0:
                    self.arreglo_botones.append(
                        TextButton(
                            o - 1,
                            self.parent,
                            i,
                            1,
                            self.sprite.rect.w - x * 2 - tabulacion,
                        )
                    )
                o += 1
            self.text_content.rect = Rect(
                x, y, self.sprite.rect.w - 80, self.text_content.total_height
            )
            y += self.text_content.total_height + spacing
            for i in self.arreglo_botones:
                i.rect.x = x + tabulacion / 2
                i.rect.y = y
                y += i.rect.h + spacing / 2
            self.img_bg = Background(self.sprite.rect.w, y).return_imagen()
            self.sprite.image = Background(self.sprite.rect.w, y).return_imagen()

            for i in self.text_content.words:
                self.sprite.image.blit(i.image, i.rect)
                self.img_bg.blit(i.image, i.rect)
            self.sprite.rect.center = (px, py)

            for i in self.arreglo_botones:
                self.sprite.image.blit(i.image, i.rect)
                self.img_bg.blit(i.image, i.rect)
                i.rect.x = self.sprite.rect.x + i.rect.x
                i.rect.y = self.sprite.rect.y + i.rect.y

        if layout_type == 2:

            self.sprite.image = load(misc_path + "cuadropop-up.png").convert_alpha()
            self.sprite.rect = self.sprite.image.get_rect()
            self.sprite.rect.w += extra_width
            self.text_content = InlineText(
                15,
                15,
                texto1,
                parent.config.get_font_size(),
                3,
                self.sprite.rect.w - 15,
                images,
            )
            self.sprite.image = Background(
                self.sprite.rect.w, self.text_content.final_width + 30
            ).return_imagen()
            self.sprite.rect.h = self.text_content.final_width + 30
            self.extra_width = self.text_content.final_width + 60
            for i in self.text_content.words:
                self.sprite.image.blit(i.image, i.rect)
            self.sprite.rect.center = (px, py)

    def popup_estatus(self):
        """
        Return whether the popup is currently visible.

        @return: True if the popup is active, False otherwise.
        @rtype: bool
        """
        if self.activo:
            return True
        else:
            return False

    def redraw_button(self):
        """Redraw the button area over the cached background (discontinued)."""
        if self.layout_type == 0:
            self.sprite.image.blit(
                self.img_bg, (self.action_btn.rect.x, self.action_btn.rect.y), self.action_btn.rect
            )
            self.sprite.image.blit(self.action_btn.img, self.action_btn.rect)
        if self.layout_type == 1:
            self.sprite.image.blit(self.img_bg, (0, 0))

    def add_to_group(self):
        """Add the popup sprite to its group and mark it as active."""
        self.activo = 1
        self.group.add(self.sprite)

    def remove_from_group(self):
        """Remove the popup sprite from its group and mark it as inactive."""
        self.activo = 0
        self.group.remove(self.sprite)

    def get_click_result(self):
        """
        Return the last click result set by handle_events().

        @return: Button index that was clicked, or -1 if no click occurred.
        @rtype: int
        """
        return self.click

    def handle_events(self, event):
        """
        Handle mouse and keyboard input for layout_type 0 and layout_type 1 popups.

        @param event: The latest pygame event.
        @type event: pygame.event.Event
        """

        teclasPulsadas = get_pressed()
        if self.layout_type == 0:
            if self.btn_rect.collidepoint(get_pos()):
                if event.type == MOUSEBUTTONDOWN and event.button == 1:
                    self.remove_from_group()
                    self.click = 0
                    return True
                else:
                    self.click = -1

            if teclasPulsadas[K_RETURN]:
                self.remove_from_group()
                self.click = 0
            else:
                self.click = -1

        if self.layout_type == 1:
            for i in self.arreglo_botones:
                if i.rect.collidepoint(get_pos()):
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        self.click = i.identificador
                    else:
                        self.click = -1
