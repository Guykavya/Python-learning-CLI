## Hint 1

For each call, first find what the argument gives for `T`. In `first([1, 2, 3])` the argument is a `list[int]`, which is a `Sequence[int]`. Match `Sequence[T]` against `Sequence[int]`: what is `T`? Then read the return hint with that `T`.

## Hint 2

`first("hello")`: a `str` is a `Sequence[str]`. `wrap(wrap(1))`: solve the inner call first (`list[int]`), and that result is the argument of the outer call. For `first([[1], [2]])` the items are lists of ints.

## Hint 3

For `G` to `J`: compute the return type as in the reveal lines, then compare it with the declared type. `int` into `float` is fine (numeric tower). In `J`, `T` must be both `int` (from `a`) and `str` (from the list): can one type be both?
