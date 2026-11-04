# Search insert position

A sorted list (duplicates allowed) and some queries. For each query `x` print the **insertion point**: the smallest index `i` such that `a[i] >= x`, or `n` if every element is smaller than `x`.
This is the index where `x` can be inserted so the list stays sorted, placing it **before** any equal elements. It is the `lower_bound`, and what `bisect_left` returns.

Write it by hand, using the half-open template: `lo = 0`, `hi = n`, `while lo < hi`, `mid = (lo + hi) // 2`. `bisect`, `index`, `count` and `in` are not allowed.

## Input

- Line 1: `n`. Line 2: `n` integers in non-decreasing order.
- Line 3: `q`. Line 4: `q` integers.

## Output

`q` lines, one insertion point each.

## Constraints

- `1 <= n <= 100000`, `1 <= q <= 100000`
- `-10^9 <= a[i], x <= 10^9`

## Example

Input:

```
6
1 3 3 5 6 9
5
3 4 0 9 10
```

Output:

```
1
3
0
5
6
```

(3 first appears at index 1. 4 would go before the 5 at index 3. 10 goes at the end, index 6.)
