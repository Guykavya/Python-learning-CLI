## Approach

Work on the tree (chapter section 19). Each `except*` clause calls, in effect, `eg.split(T)`: the
matching part (same message, same nesting, empty sub-groups removed) goes to the clause; the rest
continues to the next clause. Whatever survives every clause is re-raised at the end of the `try`
statement.

## Step by step

**Part 1.** `run()` raises the `batch` group.

1. `except* ValueError`: matching part is `batch[ValueError("bad age"), io[ValueError("bad zip")]]`.
   `g.message` is `batch` (same message as the original). Leaves in order ->
   `V: batch ['bad age', 'bad zip']`.
2. Left: `batch[DbError, io[NetError, KeyError], TypeError]`. `except* AppError`: `DbError` and
   `NetError` are subclasses of `AppError` -> `batch[DbError("db down"), io[NetError("timeout")]]` ->
   `A: batch ['db down', 'timeout']`. Its direct children are `DbError` and the sub-group `io` ->
   `A nested: ['DbError', 'ExceptionGroup']`.
3. Left: `batch[io[KeyError], TypeError]`. `except* DbError`: no `DbError` left (the `AppError`
   clause took it), so this clause does **not** run.
4. The unhandled part is re-raised at the end of the `try` statement, so `print("end of run")` is
   **skipped**.
5. The outer `except ExceptionGroup` catches it. Message `batch`, leaves `'id'` (`str` of a
   `KeyError` keeps the quotes) and `not int` -> `left: batch ["'id'", 'not int']`. (The list shows
   `"'id'"` because the string itself contains single quotes.)

**Part 2.** `NetError("solo")` is not a group, so `except*` wraps it: `ExceptionGroup("", [NetError])`
-> `solo: ExceptionGroup '' ['solo']`.

**Part 3.** The group `g` has three leaves.

1. `except* ValueError` runs -> `handling V`, then raises `RuntimeError`. That does not stop the
   other clauses.
2. `except* TypeError` runs -> `handling T`.
3. `KeyError(3)` is still unhandled. `finally` runs before anything leaves the statement -> `finally`.
4. Python raises `ExceptionGroup("", [RuntimeError("from handler"), g[KeyError(3)]])`: the raised
   exception first, then the unhandled rest (with its original message `g`) ->
   `outer: '' ['RuntimeError', 'ExceptionGroup']` and `inner: g ['3']`.

**Part 4.** Both leaves are `AppError`s -> `caught 2`. A clause ran, so `else` does not run.
Nothing is left over -> `after`.

## Output

```text
--- part 1
V: batch ['bad age', 'bad zip']
A: batch ['db down', 'timeout']
A nested: ['DbError', 'ExceptionGroup']
left: batch ["'id'", 'not int']
--- part 2
solo: ExceptionGroup '' ['solo']
--- part 3
handling V
handling T
finally
outer: '' ['RuntimeError', 'ExceptionGroup']
inner: g ['3']
--- part 4
caught 2
after
```

## Complexity

Not applicable.

## Another way

Check single steps in the REPL with `split`: `match, rest = make().split(ValueError)` gives the same
two groups as the first clause and what continues. `make().subgroup(AppError)` gives only the matching
part.
