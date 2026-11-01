import asyncio

import pytest

from solution import session


def test_normal_use():
    log = []

    async def main():
        async with session(log) as s:
            log.append(f"use open={s['open']}")
        return s

    s = asyncio.run(main())
    assert log == ["open", "use open=True", "close"], (
        f"log was {log}. Expected open, then the body, then close."
    )
    assert s == {"open": False}, f"After the block the state must be {{'open': False}}, got {s}."


def test_close_runs_when_body_raises():
    log = []

    async def main():
        async with session(log):
            log.append("use")
            raise ValueError("bad request")

    with pytest.raises(ValueError, match="bad request"):
        asyncio.run(main())
    assert log == ["open", "use", "close"], (
        f"log was {log}. The body's error is thrown in at the yield, so code after a bare yield "
        "is skipped. Put the close steps in try/finally around the yield."
    )


def test_error_is_not_swallowed():
    log = []
    reached = []

    async def main():
        async with session(log):
            raise KeyError("missing")
        reached.append("after block")

    with pytest.raises(KeyError):
        asyncio.run(main())
    assert reached == [], (
        "The code after the async with ran, so the KeyError was swallowed. Do not catch the "
        "error in your context manager (no 'except' that does not re-raise)."
    )


def test_close_runs_on_cancel():
    log = []

    async def worker():
        async with session(log):
            log.append("use")
            await asyncio.sleep(5)

    async def main():
        task = asyncio.create_task(worker())
        await asyncio.sleep(0.05)
        task.cancel()
        try:
            async with asyncio.timeout(2):
                await task
        except asyncio.CancelledError:
            pass
        return task

    task = asyncio.run(main())
    assert log == ["open", "use", "close"], (
        f"log was {log}. A cancelled task must still close the session: CancelledError is "
        "thrown in at the yield too, so 'finally' runs."
    )
    assert task.cancelled(), "The cancel must not be swallowed by the context manager."


def test_each_use_gets_its_own_state():
    async def main():
        log1, log2 = [], []
        async with session(log1) as a, session(log2) as b:
            assert a is not b, "Each session needs its own state dict; create it inside session()."
        return log1, log2

    log1, log2 = asyncio.run(main())
    assert log1 == ["open", "close"] and log2 == ["open", "close"]
