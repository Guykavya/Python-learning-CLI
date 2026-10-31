from dataclasses import dataclass


@dataclass
class Pair:
    first: object
    second: object

    def swap(self):
        return self

    def map_first(self, func):
        return self

    def map_second(self, func):
        return self


def swap_tuple(p):
    return p
