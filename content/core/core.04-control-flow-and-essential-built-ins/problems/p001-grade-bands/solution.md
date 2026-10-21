## Approach

Reject impossible marks first. Then test the bands from highest to lowest. Each `elif`
is only reached when every earlier condition was false, so one comparison per band is enough.

## Code

```python
mark = int(input())
if mark < 0 or mark > 100:
    print("invalid")
elif mark >= 90:
    print("A")
elif mark >= 75:
    print("B")
elif mark >= 60:
    print("C")
elif mark >= 40:
    print("D")
else:
    print("F")
```

## Why it works

For 82: not invalid, not `>= 90`, but `>= 75`, so `B`. The chain stops there.
The boundaries (90, 75, 60, 40) use `>=` because those marks belong to the higher band.

## Another way

`elif 75 <= mark <= 89:` with both ends written also works, and is order-independent.
It is longer and gives you more numbers to get wrong. Ordered single comparisons are the usual style.
