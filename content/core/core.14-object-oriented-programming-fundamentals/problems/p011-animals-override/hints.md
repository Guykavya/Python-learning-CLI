## Hint 1

`describe` is the same for every animal; only the sound differs. So where should `describe` live,
and what should it call to get the right sound? What does `self` refer to when you call
`Dog("Rex").describe()`, even though `describe` is written in `Animal`?

## Hint 2

```
class Animal:
    def __init__(self, name): self.name = name
    def sound(self): return "..."
    def describe(self): return f"{self.name} says {self.sound()}"

class Dog(Animal):
    def sound(self): return "Woof"
    def fetch(self): return f"{self.name} fetches the ball"

class Cat(Animal): ... sound returns "Meow"
class Cow(Animal): ... sound returns "Moo"
```
