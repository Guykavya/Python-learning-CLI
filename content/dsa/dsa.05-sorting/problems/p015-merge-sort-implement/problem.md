# Implement merge sort

Write **merge sort** from memory: split the list in two halves, sort each half recursively, then merge the two sorted halves with two pointers.
Read `n` integers and print them in ascending order. `sorted()`, `.sort()`, `heapq` and `bisect` are not allowed; the tests read your source.

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

The sorted list on one line.

## Constraints

- `1 <= n <= 200000`
- `-10^9 <= a[i] <= 10^9`

Your sort must be `O(n log n)`: the largest test has 200000 numbers and an `O(n^2)` sort will time out.

## Example

Input:

```
7
38 27 43 3 9 82 10
```

Output:

```
3 9 10 27 38 43 82
```
