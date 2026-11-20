# Read the timeline

Chapter section 7.3. This is about **PostgreSQL**'s behaviour (SQLite has no `READ COMMITTED`); you trace it on paper. A table `accounts(id, balance)` holds one row: `id = 1`, `balance = 100`. Two transactions, `T1` and `T2`, run **interleaved** in this order:

```text
 1. T1: BEGIN
 2. T1: SELECT balance FROM accounts WHERE id = 1;      -- result A
 3. T2: BEGIN
 4. T2: UPDATE accounts SET balance = 150 WHERE id = 1;
 5. T1: SELECT balance FROM accounts WHERE id = 1;      -- result B   (T2 has NOT committed)
 6. T2: COMMIT
 7. T1: SELECT balance FROM accounts WHERE id = 1;      -- result C
 8. T1: UPDATE accounts SET balance = balance + 10 WHERE id = 1;
 9. T1: COMMIT
```

Run it twice in your head: first with both transactions at **READ COMMITTED** (PostgreSQL's default), then with both at **REPEATABLE READ**.

Rules (chapter section 7.3): READ COMMITTED lets every statement see the data **committed before that statement started**. REPEATABLE READ gives the transaction **one snapshot**, taken at its first statement. In REPEATABLE READ an `UPDATE` of a row that another transaction **committed a change to after your snapshot** fails with a serialization error (`could not serialize access due to concurrent update`) and the transaction must be retried.

Write your answer in `answer.txt` in exactly these three lines (use the word `error` if step 8 fails and T1 cannot commit its update):

```text
read committed: A=<n> B=<n> C=<n> final=<balance after step 9, or error>
repeatable read: A=<n> B=<n> C=<n> final=<balance after step 9, or error>
anomaly: <name of the anomaly that READ COMMITTED allows here>
```

Do not run it.

## After you answer

1. Why is B the same in both levels? (Which anomaly would show 150 there?)
2. At READ COMMITTED, why does the update in step 8 produce 160 and not 110?
3. At REPEATABLE READ, what must the application do after the error?
