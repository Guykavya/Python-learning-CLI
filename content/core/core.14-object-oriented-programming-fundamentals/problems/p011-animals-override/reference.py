class Animal:
    def __init__(self, name):
        self.name = name

    def sound(self):
        return "..."

    def describe(self):
        return f"{self.name} says {self.sound()}"


class Dog(Animal):
    def sound(self):
        return "Woof"

    def fetch(self):
        return f"{self.name} fetches the ball"


class Cat(Animal):
    def sound(self):
        return "Meow"


class Cow(Animal):
    def sound(self):
        return "Moo"
