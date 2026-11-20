## Approach

| Line | State | Output |
|---|---|---|
| 1 | committed `[1]`; `b` reads | `[(1,)]` |
| 2 | `a` updated to 2, uncommitted; `a` reads its own change | `[(2,)]` |
| 3 | `b` reads: sees only committed data | `[(1,)]` |
| 4 | `a.commit()`: the 2 is committed; `b` reads | `[(2,)]` |
| 5 | `a` updated to 3, then `rollback()`: the change is gone; `a` reads | `[(2,)]` |
| 6 | `b` reads | `[(2,)]` |
| 7 | `b` inserted 9 (uncommitted, holds the write lock); `a` tries to insert: waits 0.2 s, fails | `database is locked` |
| 8 | `b.commit()` releases the lock; `a` inserts 10 and commits; `b` reads all | `[(2,), (9,), (10,)]` |

(Checked by running the program.)

A transaction is **private until it commits**: others see the old committed data (isolation), and a rollback leaves no trace (atomicity). Writers of the same database take turns: while one holds the lock, another waits or fails.

## Complexity

Not applicable.

## Another way

Switch the database to WAL mode (`PRAGMA journal_mode = WAL`): readers never block the writer and the writer never blocks readers, but there is still only one writer at a time.

## Why it matters

The "database is locked" error of a web app with several workers is exactly line 7: two connections want to write at once. Short transactions and a timeout (or retry, problem 28) are the cure.
