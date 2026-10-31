- Keeping `@staticmethod` on `from_string`. A staticmethod gets no `cls`, so it can only name a
  fixed class.
- Writing `cls = Vector` or `return Vector(...)` inside the classmethod. Same bug, different spelling.
- Using `self.__class__.__name__(...)`. That is a string; you cannot call it. `type(self)` (or
  `self.__class__`) is the class.
- Making `scaled` change `self.x` and `self.y` and return `self`. The task wants a new object.
- Letting `float()`'s own message escape. `"a,b"` must give `expected 'x,y', got 'a,b'`, chained
  `from` the original error.
- Forgetting `"1,2,3"`. Three parts are an error too, not "use the first two".
