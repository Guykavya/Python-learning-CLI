## Walkthrough

**touch.** `items.append(1)` mutates the caller's list: `a` becomes `[9, 1]`. Then
`items = items + [0]` builds a **new** list `[9, 1, 0]` and rebinds the local name; the
`append(2)` after it changes only that new list, which is returned. `n += 1` rebinds a local
(ints are immutable), so `b` stays 5. `word.upper()` makes a new string; `c` stays `'hi'`.
`d["seen"] = True` mutates the caller's dict; then `d = {}` rebinds, so `"lost"` goes into a
dict nobody else can see.

**extend_twice.** `+=` on a list mutates in place, and so does `extend`. `x` and `y` are one
list, so both show `[1, 3, 4]`. The function returns `None`, which is printed first.

**reset_rows.** `row = [0, 0]` only rebinds the loop variable: nothing changes. `grid[0] = ["new"]`
replaces slot 0 of the caller's outer list. `grid[1][0] = "changed"` mutates the inner list that
`inner` also refers to, so `inner` shows the change too.

**swap.** The function swaps its own local names and returns them swapped, but the caller's `m`
and `k` are untouched. (Strings are immutable, and rebinding is local.)

## The exact output

```text
[9, 1] 5 hi {'seen': True}
([9, 1, 0, 2], 6)
None [1, 3, 4] [1, 3, 4]
[['new'], ['changed', 4]] ['changed', 4]
('right', 'left') left right
```
