## Approach

- Autocommit statements create the table and insert Ada 100, Bo 50.
- Transaction 1: Ada becomes 70. At `s1`; Bo gets 80 and Cy is inserted, then `ROLLBACK TO s1` removes both. The transaction is still open. Di is inserted. At `s2` Bo is deleted; `RELEASE` keeps the delete. `COMMIT` makes Ada 70, Di 5 permanent.
- Transaction 2: Ada set to 0 and Eve inserted, then `ROLLBACK` undoes both.
- Transaction 3: `balance - 500` would be -430, violating `CHECK (balance >= 0)`: that one statement is undone and an error is printed, but the transaction stays open. The next `UPDATE` makes Ada 71 and `COMMIT` saves it.

## Code

```
1|Ada|71
4|Di|5
```

## Complexity

Transactions are about correctness, not speed, but notice cost: one `COMMIT` forces data to disk (the slow part). Many inserts inside a single transaction are much faster than the same inserts in autocommit mode.

## Another way / portable SQL

PostgreSQL has the same `SAVEPOINT`, `ROLLBACK TO`, `RELEASE`. A difference: in PostgreSQL a failed statement aborts the whole transaction until you roll back (or roll back to a savepoint), while SQLite just undoes that one statement.
MySQL InnoDB has savepoints too; MyISAM tables have no transactions at all.
