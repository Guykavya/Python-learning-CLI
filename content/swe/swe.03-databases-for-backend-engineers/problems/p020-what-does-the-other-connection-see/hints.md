## Hint 1

Line 1: connection `b` reads after `a` committed the first row: it sees `[(1,)]`. Then `a` updates the row but does not commit: who sees the new value?

## Hint 2

Line 2 is `a` reading its own uncommitted change. Line 3 is `b` reading while `a` has not committed: `b` sees the last **committed** state. After `a.commit()`, `b` sees the new value (line 4).

## Hint 3

Line 5: `a` changed to 3 and rolled back, so `a` sees 2 again. Line 7: `b` inserted without committing, so `b` holds the write lock; `a` waits 0.2 s and gets `database is locked`.
