# A generic Pair with swap and map_first

Sometimes a class has **two** independent types: a pair of "a name and a score" is
`Pair[str, int]`, a pair of "an id and a user" is `Pair[int, User]`. And operations on the pair
can **change** the types: swapping `Pair[str, int]` gives a `Pair[int, str]`.

Write in `solution.py` (use `A = TypeVar("A")`, `B = TypeVar("B")`, `C = TypeVar("C")`):

```python
@dataclass(frozen=True)
class Pair(Generic[A, B]):
    first: A
    second: B
```

with these methods:

- `swap(self) -> Pair[B, A]`: a new pair with the two values exchanged.
- `map_first(self, func: Callable[[A], C]) -> Pair[C, B]`: a new pair whose first value is
  `func(self.first)`.
- `map_second(self, func: Callable[[B], C]) -> Pair[A, C]`: same for the second value.

And one plain generic function:

- `swap_tuple(p: tuple[A, B]) -> tuple[B, A]`

Because `Pair` is used inside its own body, write the return hints as strings: `"Pair[B, A]"`.
(Python 3.14 would allow them unquoted, older versions would not. `get_type_hints` understands both.)
Import `Callable` from `collections.abc`. The tests check that the classes' two TypeVars appear
in the right **order** in each hint: that is the whole point of this exercise.

**Example**

```python
p = Pair("age", 41)        # Pair[str, int]
p.swap()                   # Pair(first=41, second='age')       Pair[int, str]
p.map_first(str.upper)     # Pair(first='AGE', second=41)       Pair[str, int]
p.map_second(float)        # Pair(first='age', second=41.0)     Pair[str, float]
swap_tuple((1, "x"))       # ('x', 1)
```
