# Trace: name mangling with double underscores

A name with **two** leading underscores and no two trailing ones, like `__pin`, gets renamed by
Python when it is written inside a class body. This is called **name mangling**. Its job is to stop
a subclass from overwriting its parent's internal names by accident; it is not a lock. Read the
program and work out what it prints.

```python
class Vault:
    __secret = "gold"
    _hint = "under the bed"

    def __init__(self, owner):
        self.owner = owner
        self.__pin = 1234

    def reveal(self):
        return self.__secret + " / " + str(self.__pin)


class SubVault(Vault):
    __secret = "silver"

    def __init__(self, owner):
        super().__init__(owner)
        self.__pin = 9999

    def own_pin(self):
        return self.__pin


v = Vault("Asha")
print(v._hint)
print(v.reveal())
try:
    print(v.__pin)
except AttributeError:
    print("no __pin")
print(v._Vault__pin)
print(sorted(vars(v)))

s = SubVault("Ben")
print(s.reveal())
print(s.own_pin())
print(sorted(vars(s)))
print(Vault._Vault__secret, SubVault._SubVault__secret)

v.__pin = 0
print(v.reveal(), v.__pin)
```

Write every printed line in `answer.txt`, one per line.

Facts you need:

- Inside the body of `class Vault`, Python rewrites every name `__x` (two leading underscores, not
  ending in `__`) to `_Vault__x`, before the code runs. Inside `class SubVault` it becomes
  `_SubVault__x`. The class used is the one whose body **contains the code**, not the class of the
  object at run time.
- Code **outside** any class (the lines at the bottom) is never rewritten. There, `v.__pin` means an
  attribute literally named `__pin`.
- One underscore (`_hint`) is only a convention ("internal, please do not touch"). Python does not
  rename it.
- `super().__init__(owner)` runs `Vault.__init__` on the same object.
- `sorted(vars(obj))` gives the names of the object's own attributes as a sorted list. In sorting,
  uppercase letters come before `_`, and `_` comes before lowercase letters.

## Example of the format

```python
class Box:
    def __init__(self):
        self.__size = 3

print(Box()._Box__size)
```

prints

```text
3
```
