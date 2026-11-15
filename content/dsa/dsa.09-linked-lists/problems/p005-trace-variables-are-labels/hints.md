## Hint 1

After the first four lines: `a` → `[1]`, `b` → `[2]`, `c` → `[3]`, `d` → `[4]`, and the arrows are `1 → 2 → 3 → None`, `4 → None`. Line `e = a` only adds a second label on `[1]`. Now do `d.next = b`: which box's arrow changes, and to where?

## Hint 2

After `a.next = c` the arrows are `1 → 3`, `4 → 2 → 3`. `b.val = 20` writes 20 into box `[2]`. `f = e.next`: `e` is still on `[1]` at this moment, so `f` goes to the box after `[1]`. Only then does `e` move to `[4]`, and `c` move to whatever comes after `[3]`.
