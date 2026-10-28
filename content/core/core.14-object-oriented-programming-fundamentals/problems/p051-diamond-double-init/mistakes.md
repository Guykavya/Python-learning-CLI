- Keeping `Printer.__init__(self, ...)` and `Scanner.__init__(self, ...)` in `Copier`. Each of them
  now calls `super()`, so the chain runs twice and you get even more connections.
- Calling `super().__init__(name)` with a positional `name` in `Printer`. For a `Copier`, the next
  class is `Scanner`, whose `__init__` takes only keywords: `TypeError`.
- Appending to `self.log` **before** calling `super().__init__`. `self.log` does not exist yet, or
  `Device` replaces it afterwards and the entry is lost.
- Taking `**kwargs` in `Device` but not passing them to `super().__init__(**kwargs)`. Then
  `Printer(name="p1", colour=False)` silently ignores the wrong keyword instead of raising `TypeError`.
- `self.connections += 1`. That reads the class attribute but **creates an instance attribute**; the
  counter on `Device` never changes.
