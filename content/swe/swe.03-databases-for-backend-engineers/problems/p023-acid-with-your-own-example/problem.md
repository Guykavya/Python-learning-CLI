# ACID with your own example

Chapter sections 6.1 and 6.6. Use the **transfer** of problem 19 (move Rs. 300 from account 1 to account 2) to explain the four letters of **ACID**. In `answer.md` write one short paragraph for each:

- **Atomicity**: what failure does it prevent? (Give a concrete crash moment.)
- **Consistency**: which rules must be true before and after? Name a constraint of the `accounts` table that helps.
- **Isolation**: what could another connection see or do while the transfer is running? Give a failure it prevents.
- **Durability**: what does the database promise after `COMMIT` returns, and how does the **write-ahead log** (or journal) make it true after a power failure?

Finish with one sentence on which of the four the application is still responsible for.
