## Hint 1

For each letter ask "what could go wrong without it?" in the transfer story: the program dies after the debit; the balance goes negative; another transfer reads a balance in the middle; the power fails right after `COMMIT`.

## Hint 2

Consistency is about **rules** (constraints, invariants such as "total money is constant"), not about the database being correct by magic.

## Hint 3

Durability: before the data pages change, the change is **written to a log and flushed** to disk. After a crash, the log is replayed (committed changes) or ignored (uncommitted).
