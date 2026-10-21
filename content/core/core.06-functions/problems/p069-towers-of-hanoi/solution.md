## Approach

The largest disc can move only when every other disc is out of the way, on the spare peg. So:
move n - 1 discs from source to spare (using target as the helper), move the largest disc, then
move the n - 1 discs from spare to target (using source as the helper). The two smaller moves are
the same problem, so recursion solves them; `n == 0` needs no moves.

## Code

```python
def hanoi(n, source="A", target="C", spare="B"):
    """Return the list of (from, to) moves that transfer n discs from source to target."""
    if n == 0:
        return []
    return (hanoi(n - 1, source, spare, target)
            + [(source, target)]
            + hanoi(n - 1, spare, target, source))
```

## Complexity

O(2ⁿ) moves, which is optimal; recursion depth n.

## Another way

There is a famous loop solution: on odd-numbered moves, move the smallest disc one peg around a
cycle; on even-numbered moves, make the only legal move not involving the smallest disc. It is
much harder to explain than the three-line recursion.
