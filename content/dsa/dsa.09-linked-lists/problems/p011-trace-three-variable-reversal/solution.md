## Approach

Follow the four lines exactly: save, flip, move `prev`, move `cur`. Then print. The reversed part is the chain that starts at `prev`.

## Expected output

```text
step 1: prev=1 cur=2 nxt=2 | reversed: 1
step 2: prev=2 cur=3 nxt=3 | reversed: 2 -> 1
step 3: prev=3 cur=4 nxt=4 | reversed: 3 -> 2 -> 1
step 4: prev=4 cur=None nxt=None | reversed: 4 -> 3 -> 2 -> 1
head is now 4 and old head 1 points to None
```

## Why

| step | `nxt` (saved) | flipped arrow | `prev` | `cur` |
|---|---|---|---|---|
| 1 | 2 | `1 -> None` | 1 | 2 |
| 2 | 3 | `2 -> 1` | 2 | 3 |
| 3 | 4 | `3 -> 2` | 3 | 4 |
| 4 | None | `4 -> 3` | 4 | None |

Each pass turns exactly one arrow around. `prev` is always the first node of the reversed part, so after the last pass it is the new head, `4`. The name `head` still labels node `1`, which became the last node, so its `next` is `None`.

If the body flipped first (`cur.next = prev`) and saved afterwards (`nxt = cur.next`), `nxt` would be `prev`, the rest of the list would be lost, and `cur = nxt` would walk back into the already reversed part (with `prev = None` at the start, the loop would end after one step and return just `1`).
