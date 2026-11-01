import asyncio

import pytest

from solution import Wallet


class CheckSpy:
    """A fake fraud check that records how many checks overlap, per wallet and overall."""

    def __init__(self, delay=0.01):
        self.delay = delay
        self.active = {}
        self.peak = {}
        self.total_active = 0
        self.total_peak = 0
        self.calls = 0

    def for_wallet(self, name):
        self.active[name] = 0
        self.peak[name] = 0

        async def check(amount):
            self.calls += 1
            self.active[name] += 1
            self.total_active += 1
            self.peak[name] = max(self.peak[name], self.active[name])
            self.total_peak = max(self.total_peak, self.total_active)
            await asyncio.sleep(self.delay)
            self.active[name] -= 1
            self.total_active -= 1

        return check


def test_balance_never_negative():
    wallet = Wallet(100)

    async def main():
        return await asyncio.gather(*(wallet.spend(30) for _ in range(10)))

    results = asyncio.run(main())
    assert wallet.balance >= 0, (
        f"Balance went to {wallet.balance}. Every task passed 'if balance < amount' before any "
        "of them subtracted, because 'await self.check(...)' lets the others run in between. "
        "Hold an asyncio.Lock around check, await and subtract."
    )
    assert results.count(True) == 3 and wallet.balance == 10, (
        f"{results.count(True)} spends succeeded, balance {wallet.balance}; expected 3 and 10."
    )


def test_exact_amounts_drain_to_zero():
    wallet = Wallet(50)

    async def main():
        return await asyncio.gather(*(wallet.spend(10) for _ in range(8)))

    results = asyncio.run(main())
    assert results == [True] * 5 + [False] * 3, (
        f"Got {results}. 50 allows five spends of 10; the first five callers (in order) win "
        "because asyncio.Lock is first come, first served."
    )
    assert wallet.balance == 0


def test_check_is_still_awaited_for_approved_spends():
    spy = CheckSpy()
    wallet = Wallet(100, check=spy.for_wallet("w"))

    async def main():
        await asyncio.gather(*(wallet.spend(40) for _ in range(4)))

    asyncio.run(main())
    assert spy.calls == 2, (
        f"The fraud check ran {spy.calls} time(s); expected 2 (two spends of 40 fit into 100). "
        "Keep 'await self.check(amount)' for each approved spend, and only for those."
    )


def test_one_wallet_handles_one_spend_at_a_time():
    spy = CheckSpy()
    wallet = Wallet(1000, check=spy.for_wallet("w"))

    async def main():
        await asyncio.gather(*(wallet.spend(1) for _ in range(5)))

    asyncio.run(main())
    assert spy.peak["w"] == 1, (
        f"{spy.peak['w']} checks of the same wallet overlapped. The lock must cover the await."
    )


def test_different_wallets_do_not_block_each_other():
    spy = CheckSpy(delay=0.02)
    a = Wallet(100, check=spy.for_wallet("a"))
    b = Wallet(100, check=spy.for_wallet("b"))

    async def main():
        await asyncio.gather(a.spend(10), b.spend(10), a.spend(10), b.spend(10))

    asyncio.run(main())
    assert spy.total_peak == 2, (
        f"Peak overlapping checks across two wallets was {spy.total_peak}; expected 2. Create "
        "the lock in __init__ (self._lock = asyncio.Lock()), not as a class attribute or a "
        "module global shared by all wallets."
    )
    assert a.balance == 80 and b.balance == 80


def test_insufficient_returns_false_without_change():
    wallet = Wallet(20)
    assert asyncio.run(wallet.spend(30)) is False, "Not enough money: return False."
    assert wallet.balance == 20, "A refused spend must not change the balance."


def test_bad_amount_raises():
    wallet = Wallet(20)
    with pytest.raises(ValueError):
        asyncio.run(wallet.spend(0))
    with pytest.raises(ValueError):
        asyncio.run(wallet.spend(-5))
    assert wallet.balance == 20


def test_lock_released_after_an_error():
    calls = []

    async def flaky(amount):
        calls.append(amount)
        if len(calls) == 1:
            raise ConnectionError("fraud service down")
        await asyncio.sleep(0)

    wallet = Wallet(100, check=flaky)

    async def main():
        with pytest.raises(ConnectionError):
            await wallet.spend(10)
        async with asyncio.timeout(1):
            return await wallet.spend(10)

    assert asyncio.run(main()) is True, (
        "After a failed check, the next spend must still work. Use 'async with self._lock' so "
        "the lock is released even when the check raises."
    )
    assert wallet.balance == 90, "The failed spend must not take money; the second one must."
