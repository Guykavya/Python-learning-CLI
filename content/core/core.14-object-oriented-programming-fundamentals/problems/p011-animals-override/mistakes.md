- Writing `describe` in every subclass. The same code three times means three places to fix later.
- Using `if isinstance(self, Dog): ... elif isinstance(self, Cat): ...` inside `describe`. Every new
  animal then needs a change in `Animal`. Overriding exists to avoid this.
- Calling `Animal.sound(self)` inside `describe`. That always gives `"..."`; `self.sound()` finds the override.
- Forgetting the base in brackets: `class Dog:`. Then `Dog("Rex")` has no `__init__` that takes a
  name and no `describe`.
- Putting `fetch` in `Animal`, so cats and cows fetch too.
