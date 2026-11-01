## Hint 1

Take the reports one at a time, each with two accounts and two threads at most.

- Report 1: draw the two threads side by side. Which lock does each hold during `pause()`, and
  which lock does each want next?
- Report 2: one thread only. `deposit_many` holds `self.lock` and calls `self.deposit`. What
  does `deposit` do first? Can a `threading.Lock` be taken twice by the same thread?
- Report 3: ten threads pass `if self.balance < amount` while the balance is still 100. Why
  does nobody notice that the money is gone?

## Hint 2

Three different cures:

```
report 1 (lock-order deadlock):
    first, second = sort (src, dst) by account number
    with first.lock: pause(); with second.lock: check funds, move money

report 2 (self-deadlock):
    either  self.lock = threading.RLock()        # same thread may re-enter
    or      a helper _add(amount) that does NOT lock, used by deposit and deposit_many

report 3 (check-then-act):
    with self.lock:
        if balance < amount: raise ValueError
        pause()
        balance -= amount
```

## Hint 3

Inside `transfer` you already hold both locks, so do not call `src.withdraw()` /
`dst.deposit()` there: with a plain `Lock` that is report 2 again. Use helpers that assume the
lock is held (or `RLock`). And `transfer(a, a, 5)` with sorted locks tries to take `a.lock`
twice: reject `src is dst` before locking.
