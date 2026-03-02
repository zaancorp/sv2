#!/usr/bin/env python

from pygame import event
from manejador import Manager
from paginas import menucfg

# from paginas import playground

def main():
    game = Manager("Sembrando para el  futuro", (1024, 572), False)
    game.changeState(menucfg.Screen(game))
    # game.changeState(playground.Screen(game))
    while game.running:
        game.handleEvents(event.get())
        game.update()
        game.draw()
    game.cleanUp()

main()
