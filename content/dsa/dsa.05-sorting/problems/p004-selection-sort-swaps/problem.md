# Selection sort and its swaps

Implement **selection sort** yourself. For `i = 0, 1, ...`, find the position `m` of the smallest value in `a[i:]` (the **leftmost** one if
there are ties), and if `m != i` swap `a[i]` and `a[m]`. Print the sorted list and the **number of swaps** you made.

`sorted()`, `.sort()`, `heapq` and `bisect` are not allowed in this problem. The tests read your source code.

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

- Line 1: the sorted list, space separated.
- Line 2: the number of swaps (a swap of an element with itself does not count).

## Constraints

- `1 <= n <= 2000`
- `-10^9 <= a[i] <= 10^9`

## Example 1

Input:

```
5
64 25 12 22 11
```

Output:

```
11 12 22 25 64
3
```

## Example 2

Input:

```
4
2 2 1 3
```

Output:

```
1 2 2 3
1
```
