from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int = 0

    def distance_to_origin(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5


@dataclass
class Product:
    name: str
    price: float
    qty: int = 0

    def total(self):
        return self.price * self.qty
