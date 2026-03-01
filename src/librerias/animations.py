#!/usr/bin/env python

import pygame

from librerias.spritesheet import SpriteSheet


class Animation(pygame.sprite.Sprite):
    """
    Esta clase permite crear y manipular animaciones a partir de una tira de imágenes.
    """

    def __repr__(self) -> str:
        return repr(
            "Animation({}, {}, {}, {}, {}, {}, {})".format(
                self.id, self.filename, self.col, self.fil, self.ck, self.loop, self.f
            )
        )

    def __init__(
        self, id, filename, col, fil, x, y, colorkey=None, loop=False, frames=1
    ):
        """
        Método inicializador de la clase.

        @param id: Identificador único para cada instancia de esta clase.
        @type id: str
        @param filename: Ruta de la imagen que se desea utilizar como animación.
        @type filename: str
        @param col: Numero de columnas que contiene la imagen.
        @type col: int
        @param fil: Numero de filas que contiene la imagen.
        @type fil: int
        @param x: Coordenada X en la que se comenzara a dibujar la animación.
        @type x: int
        @param y : Coordenada Y en la que se comenzara a dibujar la animación.
        @type y: int
        @param colorkey: Define el color utilizado como transparencia, por defecto no es necesario.
        @type colorkey: tuple
        @param loop: Si es True la animación se reproduce constantemente. Si es False
        la animación solo se reproduce solo una vez.
        @type loop: bool
        @param frames: Indica la velocidad a la que se cambian los fotogramas de la animación, siendo 1 el
        valor mas rápido.
        @type frames: int
        """
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.col = col
        self.fil = fil
        self.tipo_objeto = "animacion"
        self.filename = filename
        self.ss = SpriteSheet(filename)
        (_, _, w, h) = self.ss.sheet.get_rect()
        self.ck = colorkey
        self.fila_pos = 0
        self.rect = pygame.Rect(x, y, w / col, h / fil)
        self.rt = pygame.Rect(0, 0, w / col, h / fil)
        self.images = self.ss.load_strip(self.rt, col, fil, self.fila_pos, colorkey)
        self.i = 0
        self.loop = loop
        self.frames = frames
        self.f = frames
        self.image = pygame.Surface((0, 0))
        self.img = self.images[0]
        self.stop = False

    def update(self):
        """
        Devuelve la animación a la primera imagen. Este método es invocado al usar el método update() del grupo
        al que pertenezca esta animación.
        """
        self.i = 0
        self.image = self.images[0]
        self.stop = True

    def cambiar_rect(self, fila):
        """
        Permite cambiar la fila correspondiente a la tira de imagen de una animación.

        @param fila: La fila que se quiere mostrar en la animación.
        @type fila: int
        """
        self.fila_pos = fila
        self.images = self.ss.load_strip(
            self.rt, self.col, self.fil, self.fila_pos, self.ck
        )

    def mover(self, x):
        """
        Permite cambiar la posición en X de la animación.

        @param x: Nueva posición en X donde se desea ubicar la animación.
        @type x: int
        """
        (_, y, w, h) = self.rect
        self.rect = pygame.Rect(x, y, w, h)

    def reubicar(self, x, y):
        """
        Permite cambiar la posición en X e Y de la animación.

        @param x: Nueva posición en X donde se desea ubicar la animación.
        @type x: int
        @param y: Nueva posición en Y donde se desea ubicar la animación.
        @type y: int
        @note: Esta función puede sustituir a la función mover() mencionada anteriormente.
        """
        (_, _, w, h) = self.image.get_rect()
        self.rect = pygame.Rect(x, y, w, h)

    def cambiar_vel(self, vel):
        """
        Permite cambiar la velocidad a la que una animación cambia de fotogramas.

        @param vel: Nuevo valor de la velocidad de la animación.
        @type vel: int
        """
        self.f = vel
        self.frames = vel

    def detener(self):
        """
        Detiene la animación si esta reproduciéndose. De lo contrario no tiene efecto.
        """
        self.stop = True
        self.image = self.images[0]
        self.i = 0

    def continuar(self):
        """
        Continua la reproducción de una animación.
        """
        self.stop = False

    def repetir(self):
        """
        Repite la secuencia de una animación. A diferencia del método update(), este método se utiliza para
        volver a reproducir animaciones que solo se reproducen una vez.
        """
        self.stop = False
        self.i = 0

    def next(self):
        """
        Actualiza la imagen que se debe dibujar en pantalla cada vez que esta se actualiza.
        """
        if self.i >= len(self.images):
            if not self.loop:
                self.stop = True
            else:
                self.i = 0
        if not self.stop:
            self.image = self.images[self.i]
            self.f -= 1
            if self.f == 0:
                self.i += 1
                self.f = self.frames


class RenderAnim(pygame.sprite.Group):
    """
    Esta clase es una ligera modificación de la clase pygame.sprite.Group.
    Permite cambiar el fotograma de la imagen cada cierto tiempo al actualizar la pantalla.
    """

    def draw(self, surface):
        """
        Dibuja los miembros de un grupo de sprites sobre una superficie.

        @param surface: Superficie sobre la que se dibujaran los sprites pertenecientes a este grupo.
        @type surface: pygame.Surface
        """
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sprites:
            self.spritedict[spr] = surface_blit(spr.image, spr.rect)
            spr.next()
