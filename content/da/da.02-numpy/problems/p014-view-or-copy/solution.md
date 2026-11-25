## Approach

Track the six boxes of `a`:

1. `s = a[1:4]` is a view; `s[0] = 100` writes box 1 → `[0, 100, 2, 3, 4, 5]`.
2. `f = a[[0, 2]]` is a copy `[0, 2]`; `f[0] = -1` changes only `f` → `a` unchanged.
3. `r = a.reshape(2, 3)` is a view; `r[1, 0]` is box 1·3 + 0 = 3 → `[0, 100, 2, 30, 4, 5]`.
4. `m = a[a > 4]` copies `[100, 30, 5]`; `m[:] = 0` changes only `m` → `a` unchanged.
5. `a[a > 4] = 7`: a mask on the **left** writes into `a`. Boxes 1, 3 and 5 hold 100, 30, 5 → `[0, 7, 2, 7, 4, 7]`.
6. `s` is boxes 1..3 → `[7, 2, 7]`; `r` is all boxes as 2 × 3 → `[[0, 7, 2], [7, 4, 7]]`.
7. `f` is still `[-1, 2]` and `m` is `[0, 0, 0]` (their own memory). `f` shares no memory with `a`, `r` does: `False True`.

## Code

The expected output is in `expected.txt`, produced by running the program above.

## Complexity

The views cost O(1); `f` and `m` each copied their elements.

## Another way

When in doubt, ask NumPy: `np.shares_memory(a, x)` or `x.base is a`. The rule of thumb from Ch. 6.2: if the selection can be described by start, stop and step on every axis, it is a view; a list of positions or a mask is a copy, **except on the left of `=`**, where NumPy writes through it.
