## Hint 1

What changes between the three copies and what stays the same? The sides and the expected
answer change; the call and the `assert` stay. Those changing values become **rows**, the rest
becomes the body of one function with parameters.

## Hint 2

More rows are cheap, so add the cases a buggy version would get wrong: the same isosceles shape
with the equal sides in each of the three positions, a flat triangle `(1, 2, 3)`, zero and
negative sides, an isosceles shape that is not a triangle `(2, 2, 5)`, a long side in each
position, a barely valid one.

```
@pytest.mark.parametrize("a, b, c, expected", [ (3,3,3,"equilateral"), ... ], ids=["equilateral", ...])
def test_kind(a, b, c, expected):
    assert triangle_kind(a, b, c) == expected, f"({a}, {b}, {c}) should be {expected}"
```
