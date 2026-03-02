#!/usr/bin/env python

import pygame

from .events import EventHandler


class Character(pygame.sprite.Sprite):
    """Keyboard-controlled character sprite with collision detection and frame animation."""

    # pygame.mixer.init()
    facing_left = False
    busy = False
    colliding = False
    frames_right = {}
    frames_left = {}
    anim_time = 0
    marker_code = 0
    move_speed = 4
    frame_index = 0
    misc_path = "../imagenes/png/varios/"
    # sonido_choque = pygame.mixer.Sound("../audio/choque.ogg")
    # sonido_caminar = pygame.mixer.Sound("../audio/pasos.ogg")

    def __init__(self, x, y, image, frames):
        """
        Initialise the character sprite.

        @param x: Initial X position on screen.
        @type x: int
        @param y: Initial Y position on screen.
        @type y: int
        @param image: Path to the sprite-sheet image.
        @type image: str
        @param frames: Number of animation frames in the sprite sheet.
        @type frames: int
        """
        pygame.sprite.Sprite.__init__(self)
        self.image_paths = {
            -1: self.misc_path + "0.png",
            0: self.misc_path + "0.png",
            1: self.misc_path + "1.png",
            2: self.misc_path + "2.png",
            3: self.misc_path + "3.png",
            4: self.misc_path + "4.png",
            5: self.misc_path + "5.png",
            6: self.misc_path + "6.png",
            7: self.misc_path + "7.png",
            8: self.misc_path + "8.png",
            9: self.misc_path + "9.png",
            10: self.misc_path + "10.png",
            11: self.misc_path + "11.png",
            12: self.misc_path + "12.png",
            13: self.misc_path + "13.png",
            14: self.misc_path + "14.png",
            15: self.misc_path + "15.png",
            16: self.misc_path + "16.png",
            17: self.misc_path + "17.png",
            18: self.misc_path + "18.png",
            19: self.misc_path + "19.png",
            20: self.misc_path + "20.png",
            21: self.misc_path + "21.png",
            22: self.misc_path + "22.png",
            23: self.misc_path + "23.png",
            24: self.misc_path + "24.png",
            25: self.misc_path + "25.png",
            26: self.misc_path + "26.png",
            27: self.misc_path + "27.png",
            28: self.misc_path + "28.png",
            29: self.misc_path + "29.png",
            30: self.misc_path + "30.png",
            31: self.misc_path + "31.png",
        }
        self.pos_x = x
        self.pos_y = y
        self.anim_speed = 200
        self.eh = EventHandler()
        self.img_right = pygame.image.load(image).convert_alpha()
        self.img_left = pygame.transform.flip(self.img_right, True, False)
        self.height = self.img_right.get_height()
        self.width = self.img_right.get_width()
        self.frames = frames
        self.compute_rects()
        self.image = self.img_right
        self.sub_rect = self.frames_left[self.frame_index]
        self.rect = pygame.Rect(0, 0, 32, 32)
        self.char_rect = pygame.Rect(0, 0, 32, 32)
        self.advance_frame()

    def reset(self, x, y, image, frames, boundaries):
        """
        Reset the character to a new position, image, and collision boundaries.

        @param x: New X position.
        @type x: int
        @param y: New Y position.
        @type y: int
        @param image: Path to the new sprite-sheet image.
        @type image: str
        @param frames: Number of animation frames in the new sprite sheet.
        @type frames: int
        @param boundaries: Sprite group representing collidable boundaries.
        @type boundaries: pygame.sprite.Group
        """
        self.pos_x = x
        self.pos_y = y
        self.set_image(image)
        self.frames = frames
        self.boundaries = boundaries
        self.move_speed = 4
        self.marker_code = 0

    def reduce_speed(self):
        """Reduce the character's animation speed by 0.5."""
        self.move_speed = self.move_speed - 0.5

    def set_image(self, image):
        """
        Replace the character's sprite sheet and update the displayed frame to match the current orientation.

        @param image: Path to the new sprite-sheet image.
        @type image: str
        """
        self.img_right = pygame.image.load(image).convert_alpha()
        self.img_left = pygame.transform.flip(self.img_right, True, False)
        if self.facing_left:
            self.height = self.img_left.get_height()
            self.width = self.img_left.get_width()
            self.compute_rects()
            self.image = self.img_left
            self.sub_rect = self.frames_left[self.frame_index]
        else:
            self.height = self.img_right.get_height()
            self.width = self.img_right.get_width()
            self.compute_rects()
            self.image = self.img_right
            self.sub_rect = self.frames_right[self.frame_index]
        self.advance_frame()

    def reposition(self, pos_x, pos_y):
        """
        Move the character to the given position.

        @param pos_x: New X position.
        @type pos_x: int
        @param pos_y: New Y position.
        @type pos_y: int
        """
        self.pos_x, self.pos_y = (pos_x, pos_y)
        self.update_rects()
        self.advance_frame()

    def compute_rects(self):
        """Compute per-frame blit rectangles for both right-facing and left-facing images."""
        x = 0
        y = 0
        w = self.width / self.frames
        h = self.height
        for i in range(self.frames):
            self.frames_right[i] = pygame.Rect(x, y, w, h)
            x += w
            self.frames_left[i] = pygame.Rect(self.width - x, y, w, h)

    def set_direction(self, direction):
        """
        Change the character's facing direction and update its image accordingly.

        @param direction: "right" for right, "left" for left.
        @type direction: str
        """
        if not self.busy:
            if direction == "right":
                if self.facing_left == True:
                    self.pos_x = self.pos_x + (self.width / 4)
                self.facing_left = False
                self.image = self.img_right

            if direction == "left":
                if self.facing_left == False:
                    self.pos_x = self.pos_x - (self.width / 4)
                self.facing_left = True
                self.image = self.img_left

    def move(self, direction):
        """
        Move the character one step in the given direction.

        @param direction: "up", "down", "left", or "right".
        @type direction: str
        """
        if not self.busy:
            if direction == "up":
                self.pos_y -= self.get_animation_speed()
                # self.sonido_caminar.play()
                self.update_rects()
                self.advance_frame()

            if direction == "down":
                self.pos_y += self.get_animation_speed()
                # self.sonido_caminar.play()
                self.update_rects()
                self.advance_frame()

            if direction == "left":
                self.pos_x -= self.get_animation_speed()
                # self.sonido_caminar.play()
                self.update_rects()
                self.advance_frame()

            if direction == "right":
                self.pos_x += self.get_animation_speed()
                # self.sonido_caminar.play()
                self.update_rects()
                self.advance_frame()

    def check_collisions(self, direction):
        """
        Check for collisions with boundary sprites and reverse movement if one is detected.

        @param direction: Current movement direction.
        @type direction: str
        """
        if pygame.sprite.spritecollideany(self, self.boundaries):
            # self.sonido_caminar.set_volume(0)
            # self.sonido_choque.play()
            self.colliding = True
            if direction == "up":
                reverse_dir = "down"
            elif direction == "down":
                reverse_dir = "up"
            elif direction == "left":
                reverse_dir = "right"
            elif direction == "right":
                reverse_dir = "left"
            else:
                reverse_dir = "none"
            self.move(reverse_dir)
        else:
            # self.sonido_caminar.set_volume(100)
            self.colliding = False

    def update(self):
        """Read held arrow keys, update direction, move the character, and check collisions."""
        self.eh.update()
        if self.eh.held(pygame.K_UP):
            direction = "up"
        elif self.eh.held(pygame.K_DOWN):
            direction = "down"
        elif self.eh.held(pygame.K_LEFT):
            direction = "left"
        elif self.eh.held(pygame.K_RIGHT):
            direction = "right"
        else:
            direction = "none"
        self.set_direction(direction)
        self.move(direction)
        self.check_collisions(direction)

    def update_rects(self):
        """Recompute collision and carry rects based on the current position and orientation."""
        if self.facing_left:
            self.rect.left, self.rect.top = (
                self.pos_x + (self.width / 32) * 11,
                self.pos_y + 188,
            )
            self.char_rect.left, self.char_rect.top = (
                self.rect.left - (self.width / 4),
                self.pos_y + 188,
            )
        else:
            self.rect.left, self.rect.top = (
                self.pos_x + (self.width / 32) * 3,
                self.pos_y + 188,
            )
            self.char_rect.left, self.char_rect.top = (self.pos_x + 160, self.pos_y + 188)

    def advance_frame(self):
        """Advance the animation frame on a timer to produce a walking effect."""
        if pygame.time.get_ticks() - self.anim_time > self.anim_speed:
            self.anim_time = pygame.time.get_ticks()
            self.frame_index = self.frame_index + 1
            if self.frame_index > self.frames - 1:
                self.frame_index = 0
            if self.facing_left:
                self.sub_rect = self.frames_left[self.frame_index]
            else:
                self.rect.left + (self.width / 4)
                self.sub_rect = self.frames_right[self.frame_index]


class RenderChar(pygame.sprite.Group):
    """Sprite group that blits each character at its logical position using the current animation frame."""

    def draw(self, surface):
        """
        Blit all character sprites onto the given surface using their animation sub-rects.

        @param surface: Target surface to draw onto.
        @type surface: pygame.Surface
        """
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sprites:
            self.spritedict[spr] = surface_blit(
                spr.image, (spr.pos_x, spr.pos_y), spr.sub_rect
            )
