## Hint 1

For each line, ask: at this point, what does mypy know about `name`? Is it `str | None` or only `str`? Remember that a check only helps in the code that comes **after it on the path** that passed the check.

## Hint 2

`if name:` is false for `None` **and** for `""`, so inside that branch `name` is a plain `str`. `name or "?"` replaces both with `"?"`. An `assert name is not None` removes `None` for all the lines after it.

## Hint 3

For `G`: the `if` only prints. It does not return. After the `if` finishes, can `name` still be `None`? For `F`: the function promises `-> str`, but what does `get_name` hand back?
