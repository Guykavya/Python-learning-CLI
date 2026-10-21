## Hint 1

Which check must come first so that `101` never reaches the `A` branch?

## Hint 2

Once the invalid marks are handled, test from the top band down: `>= 90`, then `>= 75`, and so on.
Because the first true branch wins, `elif mark >= 75` already knows the mark is below 90.

## Hint 3

```
if mark < 0 or mark > 100: invalid
elif mark >= 90: A
elif mark >= 75: B
...
else: F
```
