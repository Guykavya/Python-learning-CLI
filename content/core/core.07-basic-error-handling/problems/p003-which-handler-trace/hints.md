## Hint 1

`IndexError` is not `KeyError`. Which clause is the first one that is a parent of `IndexError`?

## Hint 2

`%` by zero raises the same exception as `/` by zero. `[3, 1].index(2)` cannot find 2: which
exception does `list.index` raise? (Chapter 3 told you for `str.index`; lists behave the same.)

## Hint 3

`data["a"][-1]` is valid: a negative index counts from the end. A `NameError` matches none of the
clauses, so it leaves `attempt` and is caught by the outer `try`.
