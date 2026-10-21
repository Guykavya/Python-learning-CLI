## Hint 1

Which numbers sit on the edges of the three answers? Where does the answer change from -1 to 0, and from 0 to 1?

## Hint 2

Floats are legal input too: what should `sign(0.5)` and `sign(-0.5)` return? A function that converts to `int` first would get these wrong.

## Hint 3

```
@pytest.mark.parametrize("n, expected", [(5, 1), (1, 1), (0, 0), (-1, -1), (-5, -1), (0.5, 1), (-0.5, -1)])
def test_sign(n, expected):
    assert sign(n) == expected, f"..."
```
