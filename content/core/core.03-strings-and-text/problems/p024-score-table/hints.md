## Hint 1

Each line needs one cut at the comma. Which method does that safely? How do you remove the spaces around each part?

## Hint 2

`name, comma, score = line.partition(",")`, then `name.strip()` and `int(score)` (`int()` ignores surrounding spaces). Repeat for each of the three lines.

## Hint 3

```
n1, c, s1 = input().partition(",")
... same for lines 2 and 3 ...
print(f"{'Name':<12}{'Score':>6}")
print("-" * 18)
print(f"{n1.strip():<12}{int(s1):>6}")
...
average = (int(s1) + int(s2) + int(s3)) / 3
print(f"{'Average':<12}{average:>6.1f}")
```
