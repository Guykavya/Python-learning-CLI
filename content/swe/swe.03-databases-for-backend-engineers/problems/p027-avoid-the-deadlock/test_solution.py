import random
import threading

from solution import Bank


def run(targets, timeout=5):
    threads = [threading.Thread(target=t, daemon=True) for t in targets]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout)
    return [t for t in threads if t.is_alive()]


def test_simple_transfers_and_refusals():
    bank = Bank({1: 100, 2: 50})
    assert bank.transfer(1, 2, 30) is True
    assert bank.balances == {1: 70, 2: 80}
    assert bank.transfer(1, 2, 71) is False and bank.balances == {1: 70, 2: 80}, "Not enough money: False and no change."
    assert bank.total() == 150


def test_same_account_is_refused():
    import pytest
    bank = Bank({1: 10})
    with pytest.raises(ValueError):
        bank.transfer(1, 1, 5)


def test_opposite_transfers_do_not_deadlock():
    bank = Bank({1: 100000, 2: 100000})
    stuck = run([lambda: [bank.transfer(1, 2, 1) for _ in range(200)],
                 lambda: [bank.transfer(2, 1, 1) for _ in range(200)]])
    assert not stuck, ("Deadlock: two transfers in opposite directions waited for each other for ever. "
                       "Lock the two accounts in a fixed order (sorted ids), whatever the direction.")
    assert bank.total() == 200000 and bank.balances == {1: 100000, 2: 100000}, "200 moves each way cancel out."


def test_many_threads_on_many_accounts_conserve_the_total():
    accounts = {i: 1000 for i in range(5)}
    bank = Bank(accounts)

    def worker(seed):
        rng = random.Random(seed)
        for _ in range(300):
            a, b = rng.sample(range(5), 2)
            bank.transfer(a, b, rng.randint(1, 50))

    stuck = run([lambda s=s: worker(s) for s in range(6)], timeout=10)
    assert not stuck, "The threads did not finish: deadlock."
    assert bank.total() == 5000, f"Money was created or destroyed: total {bank.total()} instead of 5000."
    assert all(v >= 0 for v in bank.balances.values()), "A balance went negative: check and move while holding BOTH locks."
