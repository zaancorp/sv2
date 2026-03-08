#!/usr/bin/env python
"""Interactive map screen showing agricultural regions of Venezuela (screen 9)."""

import pygame

from components import screen
from components.texto import Text
from components.popups import PopUp
from components.background import Background
from components.pixelperfect import *
from components.objmask import object_mask

from paginas import pantalla8
from paginas import pantalla10

banners = [
    "banner-inf",
    "banner-siembra",
]

buttons = [
    "home",
    "back",
    "config",
]

# Absolute position of the zulia region; every other region is offset from it.
_ZULIA_X, _ZULIA_Y = 13, 140

# One entry per agricultural region, in the order they are layered in map_group:
#   (region_id, attr_name, dx_from_zulia, dy_from_zulia, img_base, text_prefix, num_paragraphs)
#
# • region_id  — string label used by object_mask and as the dispatch key
# • attr_name  — set on self so resume() and old call-sites still work (self.zulia, etc.)
# • img_base   — stem of the -des.png / -act.png image pair
# • text_prefix — first part of content.json keys: "text_N_1", "text_N_2", …
# • num_paragraphs — how many text_N_K paragraph entries exist for this region
_REGION_SPECS = [
    ("región zuliana",      "zulia",    0,    0,  "zulia",    "text_6",   3),
    ("región occidental",   "occ",     55,   -6,  "occ",      "text_5",   3),
    ("región central",      "central", 115,  37,  "central",  "text_3",   3),
    ("región insular",      "insu",    149,  -6,  "insular",  "text_10",  4),
    ("región capital",      "capital", 152,  32,  "capital",  "text_2",   4),
    ("región nor oriental", "ori",     195,  29,  "ori",      "text_8",   3),
    ("región los andes",    "andes",    23,  48,  "andes",    "text_7",   3),
    ("región los llanos",   "llanos",   26,  47,  "llanos",   "text_4",   3),
    ("región guayana",      "guayana", 140,  48,  "guayana",  "text_9",   3),
]


class Screen(screen.Screen):
    """Screen displaying a pixel-perfect clickable map of Venezuela's agricultural regions."""

    def __init__(self, parent):
        """
        Initialise the screen and build all map region mask objects.

        @param parent: Screen manager instance.
        @type parent: Manejador
        """

        self.name = "screen_9"
        super().__init__(parent, self.name)

        self.fondo_texto = False

        self.mouse = object_mask("Cursor", 850, 512, self.misc_path + "puntero.png")

        # Build all nine region masks from _REGION_SPECS.
        self.regions = {}         # region_id -> object_mask
        self.region_list = []     # ordered list used for map_group.add (preserves z-order)
        self._text_prefix = {}    # region_id -> text_prefix (for TTS key lookup)
        for region_id, attr, dx, dy, img_base, text_prefix, _count in _REGION_SPECS:
            mask = object_mask(
                region_id,
                _ZULIA_X + dx,
                _ZULIA_Y + dy,
                self.misc_path + f"{img_base}-des.png",
                self.misc_path + f"{img_base}-act.png",
            )
            self.regions[region_id] = mask
            setattr(self, attr, mask)   # e.g. self.zulia, self.capital, …
            self.region_list.append(mask)
            self._text_prefix[region_id] = text_prefix

        self.limites1 = pygame.image.load(self.misc_path + "limitemar.png").convert_alpha()
        self.limites2 = pygame.image.load(
            self.misc_path + "limitemar2.png"
        ).convert_alpha()
        self.zona_r = pygame.image.load(self.misc_path + "zona-recla.png").convert_alpha()
        self.n_estados = pygame.image.load(
            self.misc_path + "nombre-estados.png"
        ).convert_alpha()

        self.load_banners(banners)
        self.load_buttons(buttons)
        self.load_texts()
        self.bg = Background(573, 377)

        self.button_actions = {
            "home":   self.go_home,
            "config": self.go_config,
            "back":   self.go_back,
        }

    def load_texts(self):
        """Load and build the text objects for all map regions and the introductory popup."""
        font_size = self.parent.config.get_font_size()
        self.region_texts = {}  # region_id -> [Text, Text, …]
        for region_id, _attr, _dx, _dy, _img_base, text_prefix, count in _REGION_SPECS:
            texts = []
            for i in range(1, count + 1):
                key = f"{text_prefix}_{i}"
                y = 60 if i == 1 else texts[-1].y + texts[-1].total_width + 10
                texts.append(Text(490, y, self.screen_text(key), font_size, 1, 1000))
            self.region_texts[region_id] = texts

        self.popup_ins1 = PopUp(
            self.parent,
            (self.parent.text_loader.popup("screen_9", "text_1"),),
            "",
            None,
            self.popup_group,
            1,
            750,
            400,
            -100,
        )
        self.popup_ins1.add_to_group()

    def start(self):
        self.resume()

    def resume(self):
        """Reload buttons and texts if config changed, reset all map regions, then populate sprite groups."""
        if self.parent.config.is_text_change_enabled():
            self.load_buttons(buttons)
            self.load_texts()
            self.parent.config.set_text_change_enabled(False)
        self.popup_ins1.add_to_group()
        for mask in self.regions.values():
            mask.apagar()
        self.banner_group.add(self.banner_siembra, self.banner_inf)
        self.button_group.add(self.config, self.back, self.home)
        self.map_group.add(*self.region_list)
        self.speech_server.processtext(
            self.parent.text_loader.popup("screen_9", "reader_1"),
            self.parent.config.is_screen_reader_enabled(),
        )

    def _show_region(self, region_id):
        """Highlight the given region and display its text paragraphs.

        Turns off every other region mask, turns on this one, and populates
        ``word_group`` with the region's text sprites. Does not send TTS —
        callers that need TTS should call ``_announce_region`` separately.

        @param region_id: ID string of the region to display.
        @type region_id: str
        """
        for rid, mask in self.regions.items():
            if rid != region_id:
                mask.apagar()
        self.regions[region_id].iluminar()
        texts = self.region_texts[region_id]
        self.word_group.empty()
        for t in texts:
            self.word_group.add(t.words)

    def _announce_region(self, region_id):
        """Send TTS for the given region's text paragraphs.

        @param region_id: ID string of the region to announce.
        @type region_id: str
        """
        texts = self.region_texts[region_id]
        prefix = self._text_prefix[region_id]
        tts = self.screen_text(f"{prefix}_1l") + "".join(t.texto for t in texts[1:])
        self.speech_server.processtext(tts, self.parent.config.is_screen_reader_enabled())

    def go_back(self):
        self.clear_groups()
        self.parent.animation_index = 3
        self.parent.changeState(pantalla8.Screen(self.parent, 3))

    def handleEvents(self, events):
        """
        Process input events for this screen.

        @param events: Event list from the main loop.
        @type events: list
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.parent.quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.fondo_texto = False
                    self.word_group.empty()
                    self.keyboard_nav_active = True
                    self.nav_right()
                elif event.key == pygame.K_LEFT:
                    self.fondo_texto = False
                    self.word_group.empty()
                    self.nav_left()
                elif self.keyboard_nav_active and event.key == pygame.K_RETURN:
                    if self.x.obj_type == "map":
                        self.fondo_texto = True
                        self._show_region(self.x.id)
                        self._announce_region(self.x.id)
                    elif self.x.obj_type == "button":
                        self.keyboard_nav_active = False
                        self.button_actions.get(self.x.id, lambda: None)()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                lista = spritecollide_pp(self.mouse, self.map_group)
                if lista:
                    self.keyboard_nav_active = False
                    self.fondo_texto = True
                    self._show_region(lista[0].id)
                    self._announce_region(lista[0].id)
                elif pygame.sprite.spritecollideany(self.mouse, self.button_group):
                    sprite = pygame.sprite.spritecollide(self.mouse, self.button_group, False)
                    self.button_actions.get(sprite[0].id, lambda: None)()

        # When mouse is not hovering any region and keyboard nav is inactive,
        # clear the text panel (mirrors the original per-event clear).
        if not self.keyboard_nav_active:
            lista = spritecollide_pp(self.mouse, self.map_group)
            if not lista:
                self.fondo_texto = False
                for mask in self.regions.values():
                    mask.apagar()
                self.word_group.empty()
                self.text_bg_group.empty()

        self.collect_masks(self.map_group)
        self.collect_buttons(self.button_group)
        self.nav_list = self.word_list + self.mask_list + self.button_list
        self.element_count = len(self.nav_list)
        self.handle_magnifier(events)

    def update(self):
        """Update cursor position, magnifier, button tooltips, and sync the pixel-perfect mouse mask to the pointer."""
        self.mouse.update()
        self.magnifier.magnificar(self.parent.screen)
        self.button_group.update(self.tooltip_group)
        self.mouse.rect.center = pygame.mouse.get_pos()

    def draw(self):
        """Draw the background, map layers, region sprites, and text panel onto the screen manager surface."""

        self.parent.screen.blit(self.background, (0, 0))
        self.banner_group.draw(self.parent.screen)
        self.parent.screen.blit(self.zona_r, (320, 233))
        self.parent.screen.blit(self.limites1, (50, 60))
        self.parent.screen.blit(self.limites2, (305, 145))
        self.map_group.draw(self.parent.screen)
        self.popup_group.draw(self.parent.screen)
        if self.fondo_texto:
            self.parent.screen.blit(self.bg.img, (451, 55))
        self.button_group.draw(self.parent.screen)
        self.text_bg_group.draw(self.parent.screen)
        self.word_group.draw(self.parent.screen)
        self.tooltip_group.draw(self.parent.screen)
        self.parent.screen.blit(self.n_estados, (40, 95))
        if self.parent.magnifier_active:
            self.magnifier_group.draw(self.parent.screen, self.enable)
        if self.keyboard_nav_active:
            self.draw_focus_rect()
        self.draw_debug_rectangles()

    def go_to_glossary(self):
        self.parent.pushState(pantalla10.Screen(self.parent))
