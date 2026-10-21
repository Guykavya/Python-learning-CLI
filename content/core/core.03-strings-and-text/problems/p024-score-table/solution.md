## Code

```python
n1, c1, s1 = input().partition(",")
n2, c2, s2 = input().partition(",")
n3, c3, s3 = input().partition(",")
n1, n2, n3 = n1.strip(), n2.strip(), n3.strip()
s1, s2, s3 = int(s1), int(s2), int(s3)
average = (s1 + s2 + s3) / 3
print(f"{'Name':<12}{'Score':>6}")
print("-" * 18)
print(f"{n1:<12}{s1:>6}")
print(f"{n2:<12}{s2:>6}")
print(f"{n3:<12}{s3:>6}")
print("-" * 18)
print(f"{'Average':<12}{average:>6.1f}")
```

## Why the repetition is fine for now

Three lines are copied three times. Once you know loops (core.07) and lists (core.05), you will write this once for any number of students. Here the point is the formatting.

## Another way

`line.split(",")` also gives the two parts. `int(" 87")` works because `int()` ignores spaces around the digits, but `strip()` on the name is still needed.
