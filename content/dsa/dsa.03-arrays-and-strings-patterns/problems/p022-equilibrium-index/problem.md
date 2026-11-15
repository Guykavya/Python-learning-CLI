# Equilibrium index

Position `i` is an **equilibrium index** when the sum of the elements to its left equals the sum of the
elements to its right. The element at `i` itself belongs to neither side. An empty side has sum 0, so the
first and the last position can be answers too.

Print the **first** (smallest) equilibrium index, counting positions from 1. Print `-1` if there is none.

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

One line: the smallest 1-based equilibrium index, or `-1`.

## Example

Input:

```
7
-7 1 5 2 -4 3 0
```

Output:

```
4
```

At position 4 (the value 2): left `-7 + 1 + 5 = -1`, right `-4 + 3 + 0 = -1`. Position 7 is also an
equilibrium index (left sum 0, right side empty), but 4 comes first.

## Constraints

- `1 <= n <= 200000`
- `-10^9 <= a[i] <= 10^9`

Computing `sum(a[:i])` and `sum(a[i+1:])` at every position is O(n^2): too slow. Use `input()` without a prompt message.
