## Hint 1

Go statement by statement and keep a small table of what is currently in `acct`, plus a note of "what would come back if the open transaction were rolled back". Which statements are inside a transaction, and which run on their own?

## Hint 2

Questions for each block:
1. After `ROLLBACK TO s1`, which changes are gone (everything after the savepoint) and which stay (everything before it)?
2. Does `RELEASE s2` undo the `DELETE`?
3. The second transaction ends with `ROLLBACK`: what is left of both statements?
4. The third transaction: the first `UPDATE` breaks the `CHECK`. Is the transaction still open? Does the next `UPDATE` run?
