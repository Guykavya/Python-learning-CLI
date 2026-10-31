# Type aliases and the `type` statement

Long types are hard to read. A **type alias** gives a type a short name. Python 3.12+ has a
statement for it:

```python
type Point = tuple[float, float]
```

It also allows an alias to refer to **itself**, which is what you need for JSON-like data
(a JSON value can be a list of JSON values, or a dict of JSON values...).

In `solution.py` define three aliases and three functions.

**Aliases**

- `Point`: a pair of floats, `tuple[float, float]`.
- `Matrix`: a list of rows, each a list of floats, `list[list[float]]`.
- `Json`: a **recursive** alias, `dict[str, Json] | list[Json] | str | int | float | bool | None`.
  This one must be written with the `type` statement; the tests check that it is a
  `typing.TypeAliasType` and that its value is a union that includes `None`.

For `Point` and `Matrix` you may use any style: `type Point = ...`, `Point: TypeAlias = ...`, or
plain `Point = ...`.

**Functions** (their hints must use your aliases)

1. `distance(a: Point, b: Point) -> float`: Euclidean distance (`math.hypot` helps).
2. `scale(m: Matrix, k: float) -> Matrix`: a **new** matrix with every number multiplied by `k`.
3. `count_leaves(value: Json) -> int`: how many leaf values the Json contains. A leaf is a `str`,
   `int`, `float`, `bool` or `None`. Lists and dicts are not leaves; count what is inside them
   (for dicts, the values; the keys are not counted).

**Examples**

```python
distance((0.0, 0.0), (3.0, 4.0))          # 5.0
scale([[1.0, 2.0], [3.0, 4.0]], 2.0)       # [[2.0, 4.0], [6.0, 8.0]]
count_leaves({"a": [1, 2, {"b": None}], "c": "x"})   # 4
count_leaves([])                           # 0
count_leaves(5)                            # 1
```
