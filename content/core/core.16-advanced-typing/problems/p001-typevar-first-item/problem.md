# A TypeVar that keeps the element type

A function that takes "a list of anything" and returns "the first thing" should not lose the
type on the way. If you give it `list[int]` the type checker must know you get an `int` back,
and if you give it `str` you get a `str` back. `Any` or `object` would throw that
information away. A **TypeVar** keeps it.

Write three generic functions in `solution.py`. Create one `TypeVar` named `T`
(`T = TypeVar("T")`) and use it in the hints. If you use Python 3.12+, you may write
`def first[T](...)` instead.

1. `first(items: Sequence[T]) -> T`: the first item. An empty sequence raises `IndexError`.
2. `first_or(items: Sequence[T], default: T) -> T`: the first item, or `default` if the sequence is empty.
3. `last_or_none(items: Sequence[T]) -> T | None`: the last item, or `None` if the sequence is empty.

Import `Sequence` from `collections.abc`.

The tests read your hints with `typing.get_type_hints`. They check that the item type and the
return type are **the same TypeVar**, because that is what ties the answer to the question.

**Examples**

```python
first([3, 4])             # 3      a type checker says: int
first("abc")              # 'a'    a type checker says: str
first_or([], 0)           # 0
last_or_none((1, 2, 3))   # 3
last_or_none([])          # None
last_or_none([0])         # 0      careful: 0 is a real item
```
