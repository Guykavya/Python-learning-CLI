import random
import threading
import time

from solution import Account, transfer


def run_in_daemons(targets, timeout):
    """Run each target in a daemon thread, started together. Return (alive_count, errors)."""
    barrier = threading.Barrier(len(targets))
    errors = []

    def wrap(fn):
        def run():
            barrier.wait()
            try:
                fn()
            except Exception as exc:
                errors.append(exc)
        return run

    threads = [threading.Thread(target=wrap(fn), daemon=True) for fn in targets]
    for t in threads:
        t.start()
    deadline = time.monotonic() + timeout          # one deadline for ALL threads
    for t in threads:
        t.join(timeout=max(0.0, deadline - time.monotonic()))
    return sum(t.is_alive() for t in threads), errors


def test_single_thread_basics():
    a, b = Account(1, 100), Account(2, 100)
    transfer(a, b, 30)
    assert (a.balance, b.balance) == (70, 130), f"Got {(a.balance, b.balance)} after moving 30."
    a.deposit(5)
    assert a.balance == 75, "deposit(5) should add 5."
    a.withdraw(25)
    assert a.balance == 50, "withdraw(25) should take 25."


def test_withdraw_too_much_raises_and_changes_nothing():
    a = Account(1, 40)
    try:
        a.withdraw(50)
    except ValueError:
        pass
    else:
        raise AssertionError("withdraw(50) from 40 must raise ValueError.")
    assert a.balance == 40, f"A failed withdraw must not change the balance, got {a.balance}."


def test_transfer_insufficient_funds_changes_nothing():
    a, b = Account(1, 10), Account(2, 0)
    alive, errors = run_in_daemons([lambda: transfer(a, b, 50)], timeout=1)
    assert alive == 0, "transfer hung on its own. Is a lock left held after raising?"
    assert len(errors) == 1 and isinstance(errors[0], ValueError), (
        f"transfer of 50 from a balance of 10 must raise ValueError, got {errors!r}."
    )
    assert (a.balance, b.balance) == (10, 0), (
        f"Balances changed to {(a.balance, b.balance)} after a failed transfer. Check the funds "
        "BEFORE changing either balance."
    )


def test_transfer_to_same_account_is_rejected():
    a = Account(1, 100)
    alive, errors = run_in_daemons([lambda: transfer(a, a, 5)], timeout=1)
    assert alive == 0, (
        "transfer(a, a, 5) hung: it tried to take a.lock twice. A plain Lock cannot be taken "
        "twice, even by the same thread. Reject src is dst first."
    )
    assert len(errors) == 1 and isinstance(errors[0], ValueError), (
        "transfer(a, a, ...) must raise ValueError."
    )
    assert a.balance == 100, "A rejected transfer must not change the balance."


def test_deposit_many_does_not_freeze():
    a = Account(1, 0)
    alive, errors = run_in_daemons([lambda: a.deposit_many([10, 20, 30])], timeout=1)
    assert alive == 0, (
        "deposit_many froze. It holds self.lock and then calls deposit(), which waits for the "
        "same lock: a thread waiting for itself. Use an RLock, or a helper that does not lock."
    )
    assert not errors, f"deposit_many raised {errors!r}."
    assert a.balance == 60, f"deposit_many([10, 20, 30]) should add 60, got {a.balance}."


def test_opposite_transfers_do_not_deadlock():
    a, b = Account(1, 1000), Account(2, 1000)

    def a_to_b():
        for _ in range(5):
            transfer(a, b, 10)

    def b_to_a():
        for _ in range(5):
            transfer(b, a, 10)

    alive, errors = run_in_daemons([a_to_b, b_to_a], timeout=2)
    assert alive == 0, (
        "Deadlock: one thread holds account 1's lock and waits for account 2's, the other holds "
        "2's and waits for 1's. Make every transfer take the two locks in the SAME order, for "
        "example the lower account number first."
    )
    assert not errors, f"Transfers raised {errors!r}."
    assert (a.balance, b.balance) == (1000, 1000), (
        f"Balances {(a.balance, b.balance)}: equal transfers both ways should cancel out."
    )


def test_concurrent_withdrawals_never_overdraw():
    a = Account(1, 100)
    outcomes = []
    lock = threading.Lock()

    def try_withdraw():
        try:
            a.withdraw(30)
            result = "ok"
        except ValueError:
            result = "refused"
        with lock:
            outcomes.append(result)

    alive, errors = run_in_daemons([try_withdraw] * 10, timeout=4)
    assert alive == 0, "Withdrawals hung. Is the lock released when ValueError is raised?"
    assert a.balance >= 0, (
        f"Balance went to {a.balance}. All threads checked 'balance < amount' BEFORE anyone took "
        "money: the check and the change must happen under the SAME lock, in one step."
    )
    assert outcomes.count("ok") == 3 and a.balance == 10, (
        f"Expected exactly 3 successful withdrawals of 30 from 100 (balance 10), got "
        f"{outcomes.count('ok')} and balance {a.balance}."
    )


def test_many_random_transfers_keep_the_total():
    accounts = [Account(n, 500) for n in (4, 1, 3, 2)]

    def make(seed):
        rng = random.Random(seed)

        def run():
            for _ in range(8):
                src, dst = rng.sample(accounts, 2)
                try:
                    transfer(src, dst, rng.randint(1, 50))
                except ValueError:
                    pass
        return run

    alive, errors = run_in_daemons([make(s) for s in range(6)], timeout=3)
    assert alive == 0, (
        "Random transfers between 4 accounts deadlocked. Order the locks by account number, not "
        "by argument position or by the order the accounts were created."
    )
    assert not errors, f"Unexpected errors: {errors!r}."
    total = sum(acc.balance for acc in accounts)
    assert total == 2000, f"Money appeared or vanished: total is {total}, expected 2000."
    assert all(acc.balance >= 0 for acc in accounts), "No account may go below zero."
