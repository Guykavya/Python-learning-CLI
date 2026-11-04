## Approach

Apply the lower and upper bound rules to the list at each moment. Note that `insort` changes the list for the later lines.

## Expected output

```text
1 4
4 4
0 6
[10, 20, 20, 20, 25, 30, 40]
[5, 10, 20, 20, 20, 25, 30, 40]
2
2 2
0
```

## Why

`[10, 20, 20, 20, 30, 40]`: 20 occupies indices 1 to 3, so `bisect_left` gives 1 and `bisect_right` gives 4. 25 fits between 20 and 30 at index 4 for both. 5 goes to 0, 45 goes to 6 (the length).
`insort(a, 25)` inserts at index 4; `insort(a, 5)` at index 0. With plain numbers left or right makes no visible difference (equal numbers look the same); it matters for records that compare equal under a key.
In `bisect_left(a, 20, 2, 4)` the search only sees `a[2:4]` and never answers below 2 or above 4. The list is now `[5, 10, 20, 20, 20, 25, ...]`, so within indices 2 to 4 the first 20 is at 2.
With `key=len` the list of words is seen as the lengths `[3, 4, 5, 6]`, and the searched value (5 or 4) is a length too. The empty list gives 0: there is no element, so the insertion point is 0.
