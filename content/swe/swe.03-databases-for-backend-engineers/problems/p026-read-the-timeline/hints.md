## Hint 1

Which transactions can T1 "see" at each of its `SELECT`s? A transaction never sees another's **uncommitted** change in PostgreSQL. So what is B in both levels?

## Hint 2

READ COMMITTED: each statement looks at what is committed **at that moment**. At step 7 T2 has committed 150. REPEATABLE READ: T1's snapshot was taken at step 2, so it keeps seeing 100.

## Hint 3

Step 8 at READ COMMITTED: the `UPDATE` re-reads the current row (150) and adds 10: 160. At REPEATABLE READ: the row was changed and committed by T2 after T1's snapshot: serialization failure, so `final=error`. The anomaly at READ COMMITTED: the same query returned different values in one transaction.
