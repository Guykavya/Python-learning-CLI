# Build a sorted multiset

Build a small data structure from your own binary searches: a **sorted multiset** kept in one Python list that always stays sorted. Commands come one per line:

- `add x`: insert `x` (equal values may exist several times). Print nothing.
- `remove x`: remove **one** copy of `x`. Print `1` if a copy was removed, `0` if `x` was not present.
- `count_le x`: print how many stored values are `<= x`.
- `kth k`: print the `k`-th smallest stored value (1-based), or `none` if fewer than `k` values are stored.
- `ceil x`: print the smallest stored value `>= x`, or `none`.

Write `lower` and `upper` (lower and upper bound) yourself and build everything from them. `list.insert` and `del s[i]` are allowed (they move elements in one fast step). `bisect`, `insort`, `sorted`, `.sort`, `heapq`, `.index`, `.count` and `.remove` are not allowed.

## Input

- Line 1: `q`. Then `q` commands, one per line.

## Output

One line for every `remove`, `count_le`, `kth` and `ceil`, in order.

## Constraints

- `1 <= q <= 100000`, values between `-10^9` and `10^9`

## Example

Input:

```
9
add 5
add 3
add 5
count_le 5
remove 5
count_le 5
kth 2
ceil 4
remove 9
```

Output:

```
3
1
2
5
5
0
```

(After the adds the list is `[3, 5, 5]`. `kth 2` after one `5` was removed is `5`.)
