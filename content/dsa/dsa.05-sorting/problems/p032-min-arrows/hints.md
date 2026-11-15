## Hint 1

Look at the balloon whose right end is smallest. Where must an arrow be so that this balloon is burst, and where is it the most useful?

## Hint 2

At its right end `xe`: any arrow further left covers less to the right. Shoot there, discard every balloon with `xs <= xe`, and repeat with the next balloon that is not burst.

## Hint 3

```
balloons.sort(key=lambda b: b[1])
arrows = 0; last = -infinity
for xs, xe in balloons:
    if xs > last: arrows += 1; last = xe
```
