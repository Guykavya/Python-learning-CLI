## Approach

1. If the whole circle has less fuel than it costs, no start works: return `-1`.
2. Otherwise scan once with a tank. When the tank goes negative after station `i`, no station from the current start to `i` can be the start: a start `k` in that range begins with an empty tank, while the current start reached `k` with a tank `>= 0`, so `k` is never better and also fails at `i`. Restart at `i + 1`.

```python
def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    tank = 0
    start = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:              # cannot get past station i from `start`
            start = i + 1         # so no station up to i works
            tank = 0
    return start
```

Why the final `start` really works: from `start` to the end of the list the tank never goes negative, and the part before `start` has a total deficit that the positive total must cover, so the surplus collected from `start` to `n - 1` pays for the rest of the circle.

## Complexity

`O(n)` time, `O(1)` extra space.

## Another way

Compute the running sum of net gains `g[0] + ... + g[i]`. The start is the station just after the point where this running sum is **lowest** (the deepest debt): starting right after it, the debt is behind you. If the lowest running sum is reached at the last station, the start is `0` (after it comes station 0 again). It is the same idea seen as a graph of the tank level.

```python
def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    running, lowest, start = 0, 0, 0
    for i in range(len(gas)):
        running += gas[i] - cost[i]
        if running < lowest:
            lowest = running
            start = i + 1
    return start % len(gas)
```
