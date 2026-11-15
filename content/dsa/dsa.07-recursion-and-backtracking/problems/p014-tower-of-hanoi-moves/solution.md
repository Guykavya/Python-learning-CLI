## Approach

The largest disc can move only when everything else is out of the way on the spare peg. So: move `n - 1` discs to `spare`, move the big disc, move the `n - 1` discs on top of it. Each of the two sub-tasks is the same problem with one disc fewer and the roles of the pegs swapped.

## Code

```python
def hanoi(n, source="A", target="C", spare="B"):
    if n == 0:
        return []
    return (hanoi(n - 1, source, spare, target)
            + [(source, target)]
            + hanoi(n - 1, spare, target, source))
```

## Complexity

The number of moves is `M(n) = 2 M(n-1) + 1 = 2^n - 1`, and the time is proportional to that (plus list copying). The depth is only `n`.
No solution can be shorter: the biggest disc must move at least once, and each time it moves the other `n - 1` discs must be stacked on one peg.

## Another way

Append to one shared list instead of building new lists:

```python
def hanoi(n, source="A", target="C", spare="B"):
    moves = []

    def go(k, src, dst, tmp):
        if k == 0:
            return
        go(k - 1, src, tmp, dst)
        moves.append((src, dst))
        go(k - 1, tmp, dst, src)

    go(n, source, target, spare)
    return moves
```
