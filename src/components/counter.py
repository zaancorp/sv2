import pygame


class Counter:
    """Frame-rate-independent countdown timer."""

    def __init__(self, start_time, end_time, fps):
        """
        Initialise the counter.

        @param start_time: Elapsed-time value at which counting begins (milliseconds).
        @type start_time: int
        @param end_time: Elapsed-time value at which the counter is considered done (milliseconds).
        @type end_time: int
        @param fps: Frame-rate cap used when the counter clock is ticked.
        @type fps: int
        """
        self.start = start_time
        self.end = end_time
        self.fps = fps
        # Instance-level mutable state (previously class-level, causing shared-state bugs).
        self.started = False
        self.done = False
        self.elapsed = 0

    def process(self):
        """Start (or restart) the counter from start_time."""
        self.started = True
        self.clock = pygame.time.Clock()
        self.clock.tick(self.fps)
        self.elapsed = self.start

    def tick(self):
        """Advance the counter by one frame; sets done=True when end_time is reached."""
        if self.started and not self.done:
            if self.elapsed > self.end:
                self.elapsed = 0
                self.done = True
            else:
                self.elapsed += self.clock.get_time()
