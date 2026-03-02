#!/usr/bin/env python

import pygame

from components.animations import Animation, RenderAnim
from components.image import Image
from components.cursor import Cursor
from components.button import Button, RenderButton
from components.speechserver import Speechserver
from components.magnifier import Magnifier, Rendermag
from components.texto import Text
from components.assets_data import (
    backgrounds as _backgrounds,
    banners as _banners,
    images as _images,
    animations as _animations,
    buttons as _buttons,
)


class Screen(object):
    """Base class providing shared sprite groups, helpers, and lifecycle stubs for all screens."""

    # Shared resources — one instance for the entire application lifetime.
    # Intentionally class-level: the TTS server, cursor, and magnifier are
    # shared singletons that must not be recreated on every screen transition.
    speech_server = Speechserver()
    mouse = Cursor()
    magnifier = Magnifier()

    # Immutable path constants.
    pops = "./imagenes/png/popups/"
    animations_path = "./imagenes/png/animations/"
    backgrounds_path = "./imagenes/png/backgrounds/"
    banners_path = "./imagenes/png/banners/"
    buttons_path = "./imagenes/png/buttons/"
    misc_path = "./imagenes/png/varios/"

    def __init__(self, parent, screen_id):
        self.parent = parent
        self.load_background(screen_id)
        self.is_overlay = True
        self.frame_clock = pygame.time.Clock()
        self.frame_clock.tick(30)

        # Per-screen navigation state — reset fresh for every new screen.
        self.x = ""
        self.current_anim = 0
        self.focus_index = -1
        self.element_count = 0
        self.nav_list = []
        self.button_list = []
        self.word_list = []
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.enable = False
        self.first_entry = True
        self.keyboard_nav_active = False

        # Per-screen sprite groups — each screen gets its own fresh groups so
        # that pushed/popped screens never corrupt each other's sprite state.
        self.anim_group = RenderAnim()
        self.update_group = RenderAnim()
        self.image_group = RenderAnim()
        self.button_group = RenderButton()
        self.magnifier_group = Rendermag()
        self.banner_group = pygame.sprite.Group()
        self.tooltip_group = pygame.sprite.Group()
        self.text_box_group = pygame.sprite.Group()
        self.text_button_group = pygame.sprite.Group()
        self.map_group = pygame.sprite.OrderedUpdates()
        self.popup_group = pygame.sprite.OrderedUpdates()
        self.text_bg_group = pygame.sprite.GroupSingle()
        self.word_group = pygame.sprite.OrderedUpdates()
        self.debug_groups = [
            self.image_group,
            self.button_group,
            self.text_button_group,
            self.banner_group,
            self.tooltip_group,
            self.popup_group,
            self.word_group,
            self.text_box_group,
        ]

    def load_animations(self, animation_ids):
        """
        Instantiate Animation objects for each ID and bind them as instance attributes.

        @param animation_ids: IDs matching entries in the animations asset registry.
        @type animation_ids: list
        """
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
        """
        Load and convert the background surface for the given screen ID.

        @param screen_id: Key into the backgrounds asset registry.
        @type screen_id: str
        """
        self.background = pygame.image.load(
            self.backgrounds_path + _backgrounds.get(screen_id)
        ).convert()

    def load_buttons(self, button_ids):
        """
        Instantiate Button objects for each ID and bind them as instance attributes.

        @param button_ids: IDs matching entries in the buttons asset registry.
        @type button_ids: list
        """
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
        """
        Instantiate Image objects for each banner ID and bind them as instance attributes.

        @param banner_ids: IDs matching entries in the banners asset registry.
        @type banner_ids: list
        """
        for id in banner_ids:
            x, y = _banners.get(id).get("coordinates")
            filename = _banners.get(id).get("filename")
            attribute_name = id.replace("-", "_")
            setattr(self, attribute_name, Image(x, y, self.banners_path + filename))

    def load_images(self, image_ids):
        """
        Load popup image surfaces for each ID and bind them as instance attributes.

        @param image_ids: IDs matching entries in the images asset registry.
        @type image_ids: list
        """
        for id in image_ids:
            filename = _images.get(id)
            attribute_name = id.replace("-", "_")
            setattr(
                self,
                attribute_name,
                pygame.image.load(self.popups_path + filename).convert_alpha(),
            )

    def screen_text(self, key):
        """
        Return the raw string for the given key from this screen's section in content.json.

        Shorthand for ``self.parent.text_loader.get("content", self.name, key)``;
        use this for TTS / processtext calls.

        @param key: Text key within this screen's content section (e.g. "text_2").
        @type key: str
        @return: The corresponding UI string.
        @rtype: str
        """
        return self.parent.text_loader.get("content", self.name, key)

    def load_screen_texts(self, keys, x=64, y=340, text_type=1, right_limit=960, custom=False):
        """
        Create Text objects for a list of content.json keys from this screen's section.

        All texts share the same layout parameters.  Returns a dict mapping each
        key to its Text object so callers can assign them to named attributes.

        @param keys: Content keys to load (e.g. ["text_2", "text_3"]).
        @type keys: list
        @param x: Left edge of the text block in pixels.
        @type x: int
        @param y: Top edge of the text block in pixels.
        @type y: int
        @param text_type: TextType int passed to the Text constructor.
        @type text_type: int
        @param right_limit: Right edge of the text block in pixels.
        @type right_limit: int
        @param custom: Passed through to the Text constructor.
        @type custom: bool
        @return: Mapping of content key to Text object.
        @rtype: dict
        """
        content = self.parent.text_loader.screen_content(self.name)
        font_size = self.parent.config.get_font_size()
        return {
            key: Text(x, y, content[key], font_size, text_type, right_limit, custom)
            for key in keys
        }

    def clear_groups(self):
        """Empty all sprite groups belonging to this screen."""
        self.banner_group.empty()
        self.button_group.empty()
        self.text_button_group.empty()
        self.image_group.empty()
        self.word_group.empty()
        self.text_bg_group.empty()
        self.anim_group.empty()
        self.map_group.empty()
        self.tooltip_group.empty()
        self.popup_group.empty()
        self.text_box_group.empty()

    def init_audio(self):
        """Initialise the audio mixer and open channel 0 for sound effects."""
        pygame.mixer.init()
        self.audio_channel = pygame.mixer.Channel(0)
        self.audio_channel.set_endevent(pygame.locals.USEREVENT)

    def handle_magnifier(self, events):
        """
        Process magnifier events: toggle, zoom in (F5/+/-) and drag.

        @param events: Event list from the current frame.
        @type events: list
        """
        for event in events:
            if self.parent.config.is_magnifier_enabled():
                (a, b) = pygame.mouse.get_pos()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F5:
                        if self.parent.magnifier_active == False:
                            self.parent.magnifier_active = True
                            self.magnifier_group.add(self.magnifier)
                        elif self.parent.magnifier_active == True:
                            self.parent.magnifier_active = False
                            self.magnifier_group.empty()
                    if event.key == pygame.K_PLUS:
                        self.magnifier.zoom_in()
                    elif event.key == pygame.K_MINUS:
                        self.magnifier.zoom_out()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_down = True
                else:
                    mouse_down = False
                if (
                    self.magnifier.rect.collidepoint(pygame.mouse.get_pos())
                    and pygame.mouse.get_pressed()[0]
                ):
                    self.enable = True
                    if not mouse_down:
                        self.magnifier.rect.left = a - self.magnifier.w / 2
                        self.magnifier.rect.top = b - self.magnifier.h / 2
                else:
                    self.enable = False

    def set_focus_rect(self, rect=0):
        """
        Set the keyboard-focus highlight rectangle, expanded by 5 px on each side.

        Pass 0 (default) to hide the highlight rectangle.

        @param rect: Source rect from the focused element, or 0 to clear.
        @type rect: pygame.Rect | int
        """
        if rect == 0:
            self.rect = (0, 0, 0, 0)
        else:
            (x, y, w, h) = rect
            self.rect = pygame.Rect(x - 5, y - 5, w + 10, h + 10)

    def draw_focus_rect(self):
        """Draw the green keyboard-focus highlight rectangle set by set_focus_rect()."""
        pygame.draw.rect(self.parent.screen, (0, 255, 0), self.rect, 3)

    def draw(self):
        """Blit the background and all sprite groups onto the screen surface."""

        self.parent.screen.blit(self.background, (0, 0))
        self.image_group.draw(self.parent.screen)
        self.anim_group.draw(self.parent.screen)
        self.banner_group.draw(self.parent.screen)
        self.button_group.draw(self.parent.screen)
        self.text_bg_group.draw(self.parent.screen)
        self.word_group.draw(self.parent.screen)
        self.tooltip_group.draw(self.parent.screen)
        self.popup_group.draw(self.parent.screen)
        if self.parent.magnifier_active:
            self.magnifier_group.draw(self.parent.screen, self.enable)
        if self.keyboard_nav_active:
            self.draw_focus_rect()
        self.draw_debug_rectangles()

    def draw_debug_rectangles(self):
        """Draw red outlines around all debug-group sprites when DRAW_DEBUG_RECTANGLES is enabled."""
        if self.parent.DRAW_DEBUG_RECTANGLES:
            debug_rectangles = [
                object.rect for group in self.debug_groups for object in group
            ]
            for rectangle in debug_rectangles:
                pygame.draw.rect(self.parent.screen, (255, 0, 0), rectangle, 3)

    def collect_words(self, lista):
        """
        Populate word_list with all interpretable word sprites from lista.

        @param lista: All word sprites displayed on the current screen.
        @type lista: list
        """
        self.word_list = []
        [self.word_list.append(i) for i in lista if i.interpretable]

    def collect_buttons(self, lista):
        """
        Populate button_list with all buttons that have a non-empty id.

        @param lista: Button sprites present on the current screen.
        @type lista: list
        """
        self.button_list = []
        [self.button_list.append(j) for j in lista if j.id]

    def collect_masks(self, grupomask):
        """
        Populate mask_list with all collidable map sprites.

        @param grupomask: Map sprites present on the current screen.
        @type grupomask: list
        """
        self.mask_list = []
        [self.mask_list.append(mask) for mask in grupomask]

    def _announce_current(self):
        """
        Announce the current keyboard-navigation element via TTS.

        Each focusable object type (Button, palabra, object_mask) implements
        ``get_reader_text()`` to supply its own TTS string, eliminating the
        need for a obj_type string-dispatch here.
        """
        self.set_focus_rect(self.x.rect)
        self.speech_server.processtext(
            self.x.get_reader_text(),
            self.parent.config.is_screen_reader_enabled(),
        )

    def nav_right(self):
        """Advance the keyboard-navigation focus to the next element and announce it via TTS."""
        if self.focus_index < self.element_count:
            self.focus_index += 1
            if self.focus_index >= self.element_count:
                self.focus_index = self.element_count - 1
            self.x = self.nav_list[self.focus_index]
            self._announce_current()

    def nav_left(self):
        """Move the keyboard-navigation focus to the previous element and announce it via TTS."""
        if self.focus_index > 0:
            self.focus_index -= 1
            if self.focus_index <= 0:
                self.focus_index = 0
            self.x = self.nav_list[self.focus_index]
            self._announce_current()

    def start(self):
        """Load screen assets and add sprites to groups."""
        pass

    def cleanUp(self):
        """Release screen resources and remove sprites from groups."""
        pass

    def pause(self):
        """Pause screen activity when another screen is pushed on top."""
        pass

    def resume(self):
        """Resume screen activity when the screen on top is popped."""
        pass
