# Implement counting sort

When all values are integers in a small range `0..k`, you can sort without comparing elements: **count** how often each value occurs, then write out the values in order.
`sorted()`, `.sort()`, `heapq` and `bisect` are not allowed: the tests read your source.

## Input

- Line 1: `n k`.
- Line 2: `n` integers, each between `0` and `k` inclusive.

## Output

The sorted list on one line.

## Constraints

- `1 <= n <= 500000`
- `0 <= k <= 10^6`
- Time `O(n + k)`.

## Example

Input:

```
8 5
3 1 5 1 0 3 3 2
```

Output:

```
0 1 1 2 3 3 3 5
```
