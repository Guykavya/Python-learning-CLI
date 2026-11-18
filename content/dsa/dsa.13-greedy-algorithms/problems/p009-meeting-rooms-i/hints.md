## Hint 1

Sort by start. Suppose the meetings are in that order and each one ends at or before the next one starts. Can two meetings that are **not** neighbours still overlap? (Follow the chain: meeting 1 ends before meeting 2 starts, which is before meeting 2 ends, which is before meeting 3 starts...)

## Hint 2

So the only checks you need are between neighbours in sorted order. A clash is "this meeting ends **after** the next one starts": `end > next_start`. Equal is a touch, which is allowed.

## Hint 3

```
ordered = sorted(meetings)
for i in 0 .. len(ordered) - 2:
    if ordered[i].end > ordered[i + 1].start:
        return False
return True
```
