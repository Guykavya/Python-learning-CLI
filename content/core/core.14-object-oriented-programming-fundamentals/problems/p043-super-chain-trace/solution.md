## Approach

Follow the calls one at a time, like a stack (chapter sections 10 and 11).

**`t = Top("ravi")`**

1. `Top.__init__` calls `super().__init__("ravi", level=2)` first.
2. `Middle.__init__` prints `Middle init start`, then calls `super().__init__("RAVI")`.
3. `Base.__init__` prints `Base init start: RAVI`, sets `name` and `steps`, prints `Base init end`.
4. Back in `Middle`: sets `level`, prints `Middle init end: RAVI`.
5. Back in `Top`: prints `Top init end: 2`.

**`print(t.greet())`**

- `Top.greet` calls `super().greet()` **before** doing anything, so `Middle.greet` runs: it prints
  `Middle greet before`, appends `"Middle"`, and calls `Base.greet`, which appends `"Base"` and returns
  `"hello from RAVI"`. `Middle` prints `Middle greet after: hello from RAVI` and returns
  `"hello from RAVI!"`.
- `Top.greet` now appends `"Top"`, prints `Top greet got: hello from RAVI!` and returns
  `"hi from RAVI!"`, which the outer `print` shows.
- `t.steps` is `['Middle', 'Base', 'Top']`: the order in which the `append` lines ran.

**`t.run()`** is `Base.run`, but `self.describe()` starts at `Top`: `"Top>" + "Middle>" + "Base"`.
This is the template method idea: code in the base class calls methods that subclasses override.

**`print(Middle.greet(t))`** calls `Middle`'s function directly with `self = t`. `Top.greet` is
skipped. The `super()` inside `Middle.greet` still finds `Base.greet` (the class after `Middle`).
So: the two `Middle greet` lines, then `hello from RAVI!`, and `steps` gets `"Middle"`, `"Base"`.

**`m = Middle("asha", 1)`** prints the `Middle`/`Base` init lines with `ASHA`. `m.run()` starts the
lookup at `Middle`: `Middle>Base`. Finally `Base.describe(t)` calls `Base`'s version directly:
`Base`, and `m.level` is `1`.

## Output

```text
Middle init start
Base init start: RAVI
Base init end
Middle init end: RAVI
Top init end: 2
Middle greet before
Middle greet after: hello from RAVI
Top greet got: hello from RAVI!
hi from RAVI!
['Middle', 'Base', 'Top']
run: Top>Middle>Base
Middle greet before
Middle greet after: hello from RAVI
hello from RAVI!
['Middle', 'Base', 'Top', 'Middle', 'Base']
Middle init start
Base init start: ASHA
Base init end
Middle init end: ASHA
run: Middle>Base
Base 1
```

## Complexity

Not applicable.

## Another way

Add a `print` at the start and end of every method and run it; reading the result next to the code
shows the "before/after" shape of `super()` calls clearly. `Top.__mro__` shows the order that
`super()` follows: `Top`, `Middle`, `Base`, `object`.
