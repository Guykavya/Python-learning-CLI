## Hint 1

Try this in your head: `x: object = 3`, then `x + 1`. Then `x: Any = 3`, then `x + 1`. Which one does mypy accept? Which one would you trust more?

## Hint 2

For `log`, ask: does the function *use* the value in any way except printing it? For `read_config`, ask: what type do the two last lines get, and could the JSON file contain something else than they expect?

## Hint 3

The safe pattern is: take an unknown value as `object` (or return `object` from a loader), then narrow it with `isinstance` or a validator (like the TypedDict validator in an earlier problem) before using it.
