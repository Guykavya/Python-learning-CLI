## Approach

Run the `while` condition by hand for each insert: move `prev` while `prev.next` exists and its value is smaller than `val`. Write down where `prev` stopped, then link the new node after it.

## Expected output

```text
insert 4 after D : 4
insert 2 after D : 2 -> 4
insert 6 after 4 : 2 -> 4 -> 6
insert 4 after 2 : 2 -> 4 -> 4 -> 6
insert 1 after D : 1 -> 2 -> 4 -> 4 -> 6
insert 9 after 6 : 1 -> 2 -> 4 -> 4 -> 6 -> 9
```

## Why

- `4` into the empty list: no next node, `prev` stays on `D`.
- `2`: the first node `4` is not smaller than `2`, so `prev` stays on `D` and `2` becomes the new head. The dummy makes "insert before the head" the same code as any other insert.
- `6`: `2 < 6`, `4 < 6`, then there is no next node; `prev` stops on `4` and `6` goes at the end.
- second `4`: `2 < 4` moves `prev` to `2`; `4 < 4` is false, so the new `4` goes **before** the old one. With `<=` it would go after (and the insert would be *stable*: equal values keep their arrival order).
- `1`: goes before `2`, after `D`.
- `9`: walks to the last node `6`.
