- Printing `Top init end: 2` first. `Top.__init__` calls `super().__init__` before its own print.
- Writing `Base init start: ravi`. `Middle` passes `name.upper()` to `Base`.
- Writing `steps` as `['Top', 'Middle', 'Base']` (class order). `Top` appends **after** its
  `super()` call returns, so it comes last.
- `run: Base`. `self.describe()` inside `Base.run` finds `Top.describe` first, because `self` is a
  `Top`.
- Adding a `Top greet got` line for `Middle.greet(t)`. Calling `Middle.greet` directly skips
  `Top.greet` completely.
- Thinking the `super()` inside `Middle.greet` goes back to `Top`. `super()` always moves **forward**
  in the order, to `Base`.
