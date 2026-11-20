## Approach

```python
def pending(session):
    def names(objects):
        return sorted(o.name for o in objects)
    return {"new": names(session.new), "dirty": names(session.dirty), "deleted": names(session.deleted)}
```

`session.new`, `session.dirty` and `session.deleted` are read-only sets maintained by the unit of work. At flush time the session turns them into `INSERT`, `UPDATE` and `DELETE` statements in the right order (parents before children), and the sets become empty. Nothing is sent to the database before that: `pending` shows what is **about to** be sent.

Example: `customer.name = "Ravi"` on a loaded customer puts it in `dirty`; after `session.flush()` the `UPDATE` has run and `dirty` is empty again.

## Complexity

`O(objects pending)`.

## Another way

`sqlalchemy.inspect(obj)` tells the state of one object (`transient`, `pending`, `persistent`, `deleted`, `detached`) and which attributes changed (`.attrs.name.history`). `session.dirty` can include objects whose value was "set" to the same value; the real change check is `session.is_modified(obj)`.

## Why it matters

Understanding that writes are **batched** and **deferred** explains why errors appear at `commit()` and not at the line that caused them.
