## Approach

Three reports, three classic concurrency bugs:

| Report | Bug | Cure |
|---|---|---|
| opposite transfers hang | **lock-order deadlock**: T1 holds 1 and waits for 2, T2 holds 2 and waits for 1 | take locks in one global order (lower account number first) |
| `deposit_many` hangs | **self-deadlock**: a thread waits for a `Lock` it already holds | helper that assumes the lock is held, or `RLock` |
| balance -200 | **check-then-act race**: check outside the lock, change later | check and change in one critical section |

**Lock ordering.** A deadlock needs a cycle: A waits for B while B waits for A. If every
thread takes locks in the same order, no cycle can form: whoever gets lock 1 first will also be
able to get lock 2, because nobody holds 2 while waiting for 1. Sorting by `number` gives that
order. Sorting by argument position does not (that is the bug), and neither does `id()` across
processes or restarts, which is why a stable business key is better.

**Self-deadlock.** `threading.Lock` does not remember who holds it, so the owner trying again
waits forever. Two cures: `threading.RLock` (re-entrant: the owner can take it again, and must
release it as many times), or split each method into a public locking part and a private
`_add` that assumes the lock is held. The helper style is clearer, because it is obvious
which code runs under the lock.

**Check-then-act.** The decision "is there enough?" is only valid while nobody else can change
the balance, so the check, the `pause()` and the subtraction all go inside one `with
self.lock`. Now the ten withdrawals run one at a time: three succeed and seven see 10 and are
refused.

`transfer` checks `src is dst` first (sorted locks would try to take the same plain `Lock`
twice), then takes both locks in order, and calls `_take` before `_add`, so a failure raises
before anything has changed.

## Code

```python
def transfer(src, dst, amount):
    if src is dst:
        raise ValueError("cannot transfer to the same account")
    first, second = sorted((src, dst), key=lambda acc: acc.number)
    with first.lock:
        pause()
        with second.lock:
            src._take(amount)
            dst._add(amount)
```

The `Account` class (with `_add`, `_take`, the locked `withdraw` and `deposit_many` using
`_add`) is in `reference.py`.

## Complexity

Each operation is O(1) plus the `pause()`. The locks make operations on the **same** account
run one at a time; transfers between unrelated accounts still run in parallel.

## Another way

- Use `lock.acquire(timeout=1)` and back off (release everything, sleep a little, retry) when
  it fails. That turns a hang into a retry, but it is harder to get right than ordering and
  can livelock. Use it as a safety net, not as the design.
- One global bank lock for every transfer removes deadlocks completely, at the cost of all
  transfers running one at a time. For a small system that can be the right trade.
- Avoid sharing: one "bank" thread owns all balances and receives requests through a
  `queue.Queue` (p011). No locks on accounts at all.
