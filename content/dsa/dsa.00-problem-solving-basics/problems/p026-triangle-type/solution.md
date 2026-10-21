## Approach

Order the questions carefully:

1. **Validity first.** A side `<= 0` is invalid. Then find the largest side with `max(a, b, c)`.
   The sum of the other two is `a + b + c - largest`. If the largest side is at least that sum, the
   sides cannot meet (or meet flat), so print `invalid` and stop. The other two triangle inequalities
   hold automatically, because a smaller side is always less than the largest plus something positive.
2. **Type.** Test equilateral first (`a == b == c`), then "any two equal", else scalene.
3. **Right angle.** Only the largest side can be the hypotenuse. The sum of the other two squares is
   `a*a + b*b + c*c - largest*largest`. Compare with `largest*largest`. All of this is exact integer
   arithmetic, so there are no rounding problems even for sides near 10^9.

## Trace

Input `5`, `3`, `4`:

| step | values | result |
|---|---|---|
| largest | max(5, 3, 4) | 5 |
| others | 5 + 3 + 4 - 5 | 7 |
| valid? | all > 0, 5 < 7 | yes |
| type | 5 == 3? 3 == 4? 5 == 4? all no | `scalene` |
| squares | 25 + 9 + 16 - 25 = 25, largest^2 = 25 | `right` |

## Code

```python
a = int(input())
b = int(input())
c = int(input())

largest = max(a, b, c)
others = a + b + c - largest

if a <= 0 or b <= 0 or c <= 0 or largest >= others:
    print("invalid")
else:
    if a == b == c:
        print("equilateral")
    elif a == b or b == c or a == c:
        print("isosceles")
    else:
        print("scalene")

    # right angle: largest^2 equals the sum of the other two squares
    if a * a + b * b + c * c - largest * largest == largest * largest:
        print("right")
    else:
        print("not right")
```

## Complexity

A fixed number of comparisons and multiplications: O(1) time and space.

## Another way

**Sort the three values by hand** with three compare-and-swap steps: if `a > b` swap them, if `b > c` swap them,
if `a > b` swap them again. Afterwards `a <= b <= c`, so the checks become `a + b > c` and `a*a + b*b == c*c`,
which read just like the textbook rules. This is a good choice when many later checks depend on the order.
The `max` trick is shorter when you only need the largest value.

## Edge cases

- Flat triangles like `1 2 3`: largest equals the sum of the others, so invalid.
- Any zero or negative side: invalid. (In fact a non-positive side always makes `largest >= others` true as well, but checking `<= 0` explicitly states the rule clearly and costs nothing.)
- Right isosceles triangles cannot have whole-number sides (the ratio involves the square root of 2), so `isosceles` + `right` never appears here.
