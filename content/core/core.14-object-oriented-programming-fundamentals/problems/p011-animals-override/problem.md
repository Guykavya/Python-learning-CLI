# Animals: inherit and override

A subclass gets every method of its base class for free (it **inherits** them) and can replace
the ones that should behave differently (it **overrides** them). When a base-class method calls
`self.sound()`, Python uses the version of the actual object's class.

Write four classes in `solution.py`:

- `Animal(name)` stores `name`.
  - `sound()` returns `"..."`.
  - `describe()` returns `"<name> says <sound>"`, using `self.sound()`. Example: `"Rex says Woof"`.
- `Dog`, `Cat` and `Cow` inherit from `Animal`. They override **only** `sound()`, returning
  `"Woof"`, `"Meow"` and `"Moo"`. They do **not** define their own `__init__` or `describe`.
- `Dog` also has `fetch()`, returning `"<name> fetches the ball"`.

**Example**

```python
animals = [Dog("Rex"), Cat("Tom"), Cow("Gauri"), Animal("Blob")]
for a in animals:
    print(a.describe())
# Rex says Woof
# Tom says Meow
# Gauri says Moo
# Blob says ...
print(Dog("Rex").fetch())           # Rex fetches the ball
print(isinstance(Cat("Tom"), Animal))   # True
```
