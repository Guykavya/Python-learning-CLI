## Hint 1

Start with `Top("ravi")`. `Top.__init__` calls `super().__init__(...)` as its **first** line, so
nothing is printed by `Top` until `Middle.__init__` (and, inside it, `Base.__init__`) have finished.
Which name does `Base` receive: `"ravi"` or `"RAVI"`?

## Hint 2

For `t.greet()`, draw the calls as a stack:

```text
Top.greet          text = super().greet()   ...waits...
  Middle.greet     prints "before", appends "Middle", calls super().greet()
    Base.greet     appends "Base", returns "hello from RAVI"
  Middle.greet     prints "after", returns text + "!"
Top.greet          appends "Top", prints, returns text.replace(...)
```

The order of `steps` follows the order the `append` lines **run**, not the order of the classes.

## Hint 3

`t.run()` is written only in `Base`, but `self.describe()` inside it starts at `Top`. Each
`describe` adds its own name in front of what `super().describe()` returns.
`Middle.greet(t)` runs `Middle.greet` and `Base.greet` only; `Top.greet` is skipped, so no `"Top"`
is appended and no `Top greet got` line appears.
