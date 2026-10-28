## Approach

Put what all animals share in the base class and only the differences in the subclasses (chapter
section 10). `describe` is written once, in `Animal`. It calls `self.sound()`, and `self` is the
real object, a `Dog` or a `Cat`, so Python finds the subclass's `sound` first. This pattern, a base
method that calls a "hook" method the subclasses fill in, is the **template method** pattern.

Because `describe` never checks the type, a brand-new subclass (`Duck`) works without touching
`Animal` at all.

## Code

```python
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
```

## Complexity

O(1) for every method. Finding a method walks the class chain (`Dog`, then `Animal`), which is short.

## Another way

For subclasses that differ only in a fixed value, a class attribute is enough:
`class Dog(Animal): noise = "Woof"` and `describe` uses `self.noise`. A method is the better choice
once the answer needs computing (for example, a sound that depends on the animal's mood). In section 16
you will make `Animal.sound` an abstract method, so forgetting to override it is an error.
