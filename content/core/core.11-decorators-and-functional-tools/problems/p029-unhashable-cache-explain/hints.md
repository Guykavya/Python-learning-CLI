## Hint 1

`lru_cache` uses a dict inside. What must be true of anything you use as a dict key? Try
`{[1, 2]: "x"}` in the REPL.

## Hint 2

Structure: (1) dict + hash, (2) a changing key breaks the dict, (3) `tuple(...)` at the call
site or a wrapper that converts, (4) the result depends on something that is not an argument:
explain "pure function" in one sentence.
