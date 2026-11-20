## Approach

| Step | What happens | Output |
|---|---|---|
| 1 | `s1` has an empty map: `SELECT` the row, create the object | `queries = 1` |
| 2 | the row is in `s1`'s map: return the same object, no SQL | `same = True queries = 0` |
| 3 | `s2` has its own map: `SELECT`, a **different** object for the same row | `same = False queries = 1` |
| 4 | `expire(a)` runs no SQL; `a.name` reloads the row (one `SELECT`); `b` is still the same object as `a` | `same = True queries = 1` |
| 5 | `commit()` expires everything; `a.name` reloads | `queries = 1` |
| 6 | `get` finds the fresh `a` in the map | `same = True queries = 0` |

(Checked by running the program.)

The identity map guarantees **one object per row per session**, so changes made through one reference are visible through all of them, and the session can detect which objects changed (the unit of work). It also means a long-lived session may show **stale** data: another session's change is invisible until you `expire` or `refresh`.

## Complexity

Not applicable.

## Another way

`session.refresh(obj)` reloads at once; `Session(engine, expire_on_commit=False)` keeps loaded values after a commit (useful when you return objects after the session closes, but they may be stale).

## Why it matters

Knowing when a query happens explains most "why is this slow" and "why is this stale" questions about the ORM.
