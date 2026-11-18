# Gas station

There are `n` stations on a circular road. At station `i` you can fill up `gas[i]` litres; driving from station `i` to station `i + 1` (and from the last station back to station 0) costs `cost[i]` litres. Your tank starts **empty** and has no size limit.

Write `can_complete_circuit(gas, cost)` that returns the index of the station where you must start to drive once all the way round, or `-1` if no start works (chapter section 11).

The inputs are chosen so that **at most one** start works (as on the real site).

## Example

```python
>>> can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2])
3
>>> can_complete_circuit([2, 3, 4], [3, 4, 3])
-1
>>> can_complete_circuit([5], [4])
0
```

In the first example, starting at station 3 the tank after each drive is `4 - 1 = 3`, `3 + 5 - 2 = 6`, `6 + 1 - 3 = 4`, `4 + 2 - 4 = 2`, `2 + 3 - 5 = 0`: never negative.

## Constraints

- `1 <= n <= 10**5`, `0 <= gas[i], cost[i] <= 10**4`.
- `O(n)`: trying every start and driving round from each is `O(n^2)` and too slow.

## Think about

You start at `s` and the tank first goes negative after station `i`. Why can no station between `s` and `i` be the answer either?
