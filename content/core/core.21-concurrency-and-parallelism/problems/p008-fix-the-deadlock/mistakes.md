- Ordering the locks by argument position ("always lock `src` first"). That is the original
  bug: `transfer(a, b)` and `transfer(b, a)` still lock in opposite orders.
- Ordering by `id(account)`. It works inside one run, but `number` is stable and readable,
  and makes the order easy to explain in a code review.
- Calling `src.withdraw()` and `dst.deposit()` inside `transfer` while holding the locks. With
  a plain `Lock` that self-deadlocks; with an `RLock` it works but hides what is locked.
- Moving the balance check of `withdraw` inside the lock but leaving `pause()` and the
  subtraction outside it. The lock must cover check **and** change.
- Removing the `pause()` calls. The bugs stay; they only become rare, which is worse.
- Changing `src` before checking that it has enough money, then trying to undo it. Check first,
  then change both.
- Forgetting `transfer(a, a, ...)`: with ordered plain locks the thread waits for itself.
