from dataclasses import dataclass


class Point:
    def __init__(self, x, y=0):
        self.x = x
        self.y = y

    def distance_to_origin(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5


class Product:
    pass
