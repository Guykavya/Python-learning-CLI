## Approach

| Step | Run 1: no claim | Run 2: with a claim | Run 3: claim, D1 dies after claiming 2 |
|---|---|---|---|
| D1 read | `[1, 2, 3]` | same | same |
| D1 next | sends item 1 (ana=1) | claims 1, sends (ana=1) | same |
| D2 read | pending `[2, 3]` | same | same |
| D1 next | sends item 2 (ben=1) | claims 2, sends (ben=1) | claims 2, **dies** |
| D2 next | sends item 2 **again** (ben=2) | item 2 is claimed: skip | skip (claimed by the dead D1) |
| D1 next | sends item 3 (cy=1) | claims 3, sends (cy=1) | dead |
| D2 next | sends item 3 **again** (cy=2) | item 3 is claimed: skip | claims 3, sends (cy=1) |
| **Result** | ana=1 ben=2 cy=2 | ana=1 ben=1 cy=1 | ana=1 **ben=0** cy=1 |

The lessons of chapter 9.5: without a claim two dispatchers do **the same work** (and duplicates reach the users unless the **idempotency key** `outbox-<id>` makes the mailer ignore the repeat, which is why the key is there). A claim (an atomic `UPDATE ... WHERE claimed_by IS NULL`, or `SELECT ... FOR UPDATE SKIP LOCKED` in PostgreSQL) gives single processing, but a claim that never expires turns a crashed worker into a **lost** message: add a **lease** (`claimed_at` plus a timeout) so another dispatcher can take the claim over, exactly like the `JobQueue` of swe.08.

## Cost

Reading only. Rerun the program with the script reordered to see that the result depends on the interleaving: that is what makes concurrency bugs hard to reproduce, and why you design the protocol (claim, lease, idempotency) instead of hoping.

## Another way

Run **one** dispatcher (a single process or a leader elected with a lock) and avoid the problem; scale it only when the outbox backlog says you must.
