## Hint 1

For each session you must remember three things, not one. Which values do you need to answer "has it been idle too long?" and "is it too old?" at any later moment? Write them down before coding.

## Hint 2

Put the expiry logic in **one** private helper that returns the live row or `None` (and deletes dead rows). Then `get` and `rotate` both call it, so they cannot disagree about boundaries. `get` additionally updates the "last seen" time; a failed `get` must change nothing.

For `rotate`: destroy the old row, build a new row with a new id, copy `created` from the old row, set `seen` to now.

## Hint 3

```text
row = {"user", "created", "seen"}

_live(sid):
    row = rows.get(sid); if none -> None
    if now - row.seen >= idle  or  now - row.created >= absolute: delete row; return None
    return row

get(sid):    row = _live(sid); if None return None; row.seen = now; return row.user
rotate(old, user=None): row = _live(old); if None return None
                        delete old; new id; rows[new] = (user or row.user, row.created, now); return new
```
