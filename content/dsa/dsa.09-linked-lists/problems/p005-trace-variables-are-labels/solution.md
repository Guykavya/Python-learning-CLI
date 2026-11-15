## Approach

Keep two separate things on paper: the **boxes with their arrows** (nodes and `next`), and the **labels** (variables). Assignments to a plain name move a label; assignments to `.next` or `.val` change a box.

## Expected output

```text
a: 1 -> 3
b: 20 -> 3
c: None
d: 4 -> 20 -> 3
e: 4 -> 20 -> 3
f: 3
True True True
```

## Why

| Line | Effect |
|---|---|
| `b = a.next`, `c = b.next` | labels on `[2]` and `[3]` |
| `d = ListNode(4)` | a new box `[4] → None` |
| `e = a` | a second label on `[1]` |
| `d.next = b` | arrow of `[4]` now goes to `[2]`: `4 → 2 → 3` |
| `a.next = c` | arrow of `[1]` now goes to `[3]`: `1 → 3`; nothing else points from `[1]` to `[2]` |
| `b.val = 20` | box `[2]` now holds 20; `d`'s chain shows it too |
| `f = e.next` | `e` is on `[1]`, so `f` is on `[3]` |
| `e = d` | the label `e` moves to `[4]`; box `[1]` is still labelled by `a` |
| `c = c.next` | `[3]`'s arrow is `None`, so `c` is `None`; no box changes |

`a.next is f`: both are box `[3]`. `e is d`: the same box `[4]`. `d.next is b`: `[4]`'s arrow goes to `[2]`, labelled `b`. All three are `True`.
