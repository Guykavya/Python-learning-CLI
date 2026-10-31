import functools


class Recorder:
    def __init__(self, func):
        self.func = func
        self.calls = []

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
