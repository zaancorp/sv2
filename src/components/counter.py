import pygame


class Counter:
    started = False
    done = False
    elapsed = 0

    def __init__(self, start_time, end_time, fps):
        self.start = start_time
        self.end = end_time
        self.fps = fps

    def process(self):
        self.started = True
        self.clock = pygame.time.Clock()
        self.clock.tick(self.fps)
        self.elapsed = self.start

    def tick(self):
        if self.started and not self.done:
            if self.elapsed > self.end:
                self.elapsed = 0
                self.done = True
            else:
                self.elapsed += self.clock.get_time()
            print(self.elapsed)


# def main():
#    active = False
#    p = pygame.display.set_mode((400, 400))
#    cron = contador(5000, 10000, 1)
#
#    while active != True:
#        for event in pygame.event.get():
#            if event.type == pygame.QUIT:
#                active = True
#
#            if event.type == pygame.KEYDOWN:
#                if event.key == pygame.K_F1:
#                    cron.process()
#
#        cron.contar()
#        pygame.display.update()
#        pygame.time.Clock().tick(1)
# main()
