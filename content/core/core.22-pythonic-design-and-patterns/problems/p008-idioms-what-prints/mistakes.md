- Thinking `config.get("a", default())` skips `default()` because the key exists. Arguments are
  evaluated first; `calls` has two entries by the time `len(calls)` runs.
- Forgetting `repr` adds quotes: `'guest'`, not `guest`.
- Sorting by key and then shuffling ties: `sorted` is stable, ties keep the input order (also with `reverse=True`).
- Computing the Fibonacci step as `a = b; b = a + b`. Tuple assignment uses the OLD `a`.
- Saying `[[0]*2]*2` makes two lists. It makes two references to one list.
- Believing `all([])` is `False` because "there is nothing". Nothing is false, so it is `True`.
- Thinking `y += [4]` makes a new list like `y = y + [4]`. For lists `+=` changes the same object.
