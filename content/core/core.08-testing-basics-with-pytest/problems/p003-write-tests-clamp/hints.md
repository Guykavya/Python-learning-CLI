## Hint 1

Which three situations does `clamp` have: below the range, inside it, above it? Write one test for each.

## Hint 2

Bugs hide at the edges. What should `clamp(0, 0, 10)` and `clamp(10, 0, 10)` return? What happens with negative numbers, as in `clamp(-5, -10, -1)`?

## Hint 3

```
def test_below():   assert clamp(-5, 0, 10) == 0
def test_above():   assert clamp(15, 0, 10) == 10
def test_inside():  assert clamp(5, 0, 10) == 5
def test_on_edges(): clamp(0,0,10) and clamp(10,0,10)
def test_negative_range(): clamp(-5, -10, -1) == -5, clamp(-20,-10,-1) == -10
```
