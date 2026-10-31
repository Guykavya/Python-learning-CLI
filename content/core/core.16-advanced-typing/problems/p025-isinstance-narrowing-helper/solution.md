## Approach

Narrowing means the checker follows your `if` tests. After `if value is None: return 0` the type
of `value` is `int | str`. After `if isinstance(value, str): return int(value)` it is just `int`.
So the last line `return value` is accepted for `-> int`. Each function is a chain of such
tests; the final branch needs no test because the checker already knows what remains.

Test for `0` and `""` with `is None` or `isinstance`, never with `if not value`: both are falsy
but valid values.

## Code

```python
def to_int(value: int | str | None) -> int:
    if value is None:
        return 0
    if isinstance(value, str):
        return int(value)
    return value


def describe(value: int | str | list[int]) -> str:
    if isinstance(value, int):
        return f"int {value}"
    if isinstance(value, str):
        return f"str {value!r}"
    return f"list of {len(value)}"


def total_length(items: list[str | list[str]]) -> int:
    total = 0
    for item in items:
        if isinstance(item, str):
            total += len(item)
        else:
            total += sum(len(s) for s in item)
    return total


def first_text(values: list[int | str]) -> str | None:
    for v in values:
        if isinstance(v, str):
            return v
    return None
```

## Complexity

All four are O(n) in the size of the data (`to_int` and `describe` are O(1) except for `int(...)`/`len`).

## Another way

`match` statements narrow too (`case str():`, `case int():`, `case None:`). `first_text` can be
`next((v for v in values if isinstance(v, str)), None)`, which narrows the same way inside the
generator; the loop is just easier to read for a first version.
