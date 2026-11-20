## Model answer

**Atomicity.** The transfer is *all or nothing*. Without it, the program (or the machine) could stop **after the debit and before the credit**: Rs. 300 would have left account 1 and arrived nowhere. With a transaction, the database undoes the debit if the transaction is not committed: after a crash or an exception, both balances are as before.

**Consistency.** A transaction takes the database from one **valid** state to another. Valid means the rules hold: `balance_paise >= 0` (a `CHECK` constraint), the accounts exist (foreign keys), and the application invariant "the total of all balances is unchanged by a transfer". A transfer that would make a balance negative is refused and rolled back, so the invalid state never becomes visible.

**Isolation.** Concurrent transactions do not see each other's half-done work. While the transfer has debited but not credited, another connection must not read a total that is Rs. 300 short or spend the money that is being moved (a lost update). Isolation makes concurrent transactions behave as if they ran one after the other (to the degree of the isolation level).

**Durability.** After `COMMIT` returns, the transfer **survives** a crash or power failure. The database writes the change to the **write-ahead log** (or rollback journal) and flushes it to disk **before** it reports success; after a restart it replays the committed entries from the log and discards the uncommitted ones, so a committed transfer is never lost.

**What the application must still do:** consistency rules that are not written as constraints (for example "no transfer above the daily limit") are the application's job; and it must wrap related changes in one transaction, because the database cannot guess which statements belong together.

**Checklist: your answer should mention**
- [ ] **atomicity**: crash between debit and credit; all or nothing
- [ ] **consistency**: constraints/invariants (`CHECK balance >= 0`, total unchanged)
- [ ] **isolation**: others do not see half-done work (e.g. lost update / inconsistent read)
- [ ] **durability**: survives crash after `COMMIT`; **write-ahead log** flushed before success
- [ ] the application chooses the transaction boundary and some rules
