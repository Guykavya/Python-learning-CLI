import time


class Timer:
    def __init__(self, clock=time.perf_counter):
        self.clock = clock
        self.running = False

    # TODO: __enter__, __exit__ and the elapsed property
