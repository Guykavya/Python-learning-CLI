# Aggressive cows

A farmer has `n` stalls on a line at the given positions (not necessarily sorted, all different) and `c` cows. The cows fight if they are too close, so he wants to put them in `c` different stalls so that the **smallest distance between any two cows is as large as possible**.
Print that largest possible smallest distance.

Hint for the check: for a distance `d`, sort the stalls, put the first cow in the first stall, and then always put the next cow in the **first stall at least `d` away** from the last cow. If you place `c` cows, distance `d` is possible.
Bigger `d` makes it harder, so "possible" is True...True False...False: you search for the **last True**. In that case the half-open template needs `mid = (lo + hi + 1) // 2` (round up). Think about why.

## Input

- Line 1: `n c`.
- Line 2: `n` positions.

## Output

One integer.

## Constraints

- `2 <= c <= n <= 100000`
- `0 <= position <= 10^9`, all positions different

## Example

Input:

```
5 3
1 2 8 4 9
```

Output:

```
3
```

(Cows at 1, 4, 8 have distances 3 and 4, so the smallest is 3. Distance 4 fails: cows at 1 and 8 force the third cow to 12 or more, and there is no such stall.)
