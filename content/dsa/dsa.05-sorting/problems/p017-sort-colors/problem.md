# Sort colors (Dutch flag)

A list contains only the values `0`, `1` and `2` (three colours). Print it sorted. Do **not** use `sorted()`, `.sort()`, `heapq` or `bisect`:
count the values, or do the classic one-pass **Dutch national flag** partition with three pointers `lo`, `i`, `hi`.

## Input

- Line 1: `n`.
- Line 2: `n` values, each `0`, `1` or `2`.

## Output

The sorted list on one line.

## Constraints

- `1 <= n <= 500000`

## Example

Input:

```
6
2 0 2 1 1 0
```

Output:

```
0 0 1 1 2 2
```
