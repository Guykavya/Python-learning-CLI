## Hint 1

Draw the group from `make()` as a tree, then go clause by clause and **cross out** leaves:

```text
batch
├── ValueError("bad age")
├── DbError("db down")
├── io
│   ├── NetError("timeout")
│   ├── KeyError("id")
│   └── ValueError("bad zip")
└── TypeError("not int")
```

`except* ValueError` takes both `ValueError`s (one of them is inside `io`). What is still left for
`except* AppError`? Is `DbError` an `AppError`? Is anything left for `except* DbError`?

## Hint 2

After the clauses of `run()`, something is still unhandled. Is `print("end of run")` reached?

In part 3, the `ValueError` clause raises. Do the other clauses still run? Does `finally` run? The new
`RuntimeError` and the unhandled leaves end up together in one new group with message `''`: which comes
first?

In part 4, every leaf is an `AppError`. Does `else` run when an `except*` clause ran?
