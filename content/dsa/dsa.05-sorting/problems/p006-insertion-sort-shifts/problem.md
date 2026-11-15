# Insertion sort and its shifts

Implement **insertion sort** yourself and print the sorted list and the **number of shifts** (every time you copy `a[j]` one place to the right).
`sorted()`, `.sort()`, `heapq` and `bisect` are not allowed here; the tests read your source.

Use a strict comparison (`a[j] > key`) so equal values never move past each other.

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

- Line 1: the sorted list.
- Line 2: the number of shifts. It always equals the number of inversions (pairs `i < j` with `a[i] > a[j]`).

## Constraints

- `1 <= n <= 3000`

## Example

Input:

```
6
4 3 2 10 12 1
```

Output:

```
1 2 3 4 10 12
8
```
