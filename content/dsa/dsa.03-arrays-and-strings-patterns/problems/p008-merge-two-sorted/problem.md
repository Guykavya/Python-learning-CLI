# Merge two sorted arrays

Two arrays are each sorted in non-decreasing order. Print all their elements as one sorted list.

Do it the way merge sort does, **without** `sort()` or `sorted()`: keep a pointer `i` into the first array and `j`
into the second. At each step take the smaller of `a[i]` and `b[j]` and move that pointer. When one array runs out,
copy the rest of the other.

(The tests only see your output, so `sorted(a + b)` would also pass. Write the merge anyway: it is O(n + m) and it
is the heart of merge sort and of many later problems.)

## Input

- Line 1: `n`.
- Line 2: `n` integers, sorted (an empty line when `n = 0`).
- Line 3: `m`.
- Line 4: `m` integers, sorted (an empty line when `m = 0`).

## Output

One line with all `n + m` values in non-decreasing order, separated by spaces. If both arrays are empty, print an
empty line.

## Example

Input:

```
4
1 4 4 9
3
2 4 10
```

Output:

```
1 2 4 4 4 9 10
```

## Constraints

- `0 <= n, m <= 200000`
- `-10^9 <= values <= 10^9`
