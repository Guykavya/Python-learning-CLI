# Avoid the deadlock

Chapter section 7.6. A `Bank` keeps balances in memory with **one lock per account**. `transfer(src, dst, amount)` must hold the locks of **both** accounts while it moves money. `starter.py` locks `src` first and then `dst`.

Thread 1 transfers 1 -> 2 (locks 1, then waits for 2). Thread 2 transfers 2 -> 1 (locks 2, then waits for 1). Each holds the lock the other needs: a **deadlock**: both wait for ever.

Fix `transfer` so that it can never deadlock: always take the two locks in a **fixed global order** (by account id, lowest first), whichever way the money flows. Keep the rest of the behaviour:

- `src == dst` raises `ValueError`;
- not enough money: return `False` and change nothing; otherwise move the amount and return `True`;
- the **total** of all balances never changes.

The test runs opposite transfers in two threads, 200 times each, and waits at most 5 seconds for them to finish: a deadlock fails the test.
