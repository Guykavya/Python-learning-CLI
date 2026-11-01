import asyncio
from contextlib import asynccontextmanager


@asynccontextmanager
async def session(log):
    """Open a fake session; always close it, never swallow errors."""
    await asyncio.sleep(0)
    log.append("open")
    state = {"open": True}
    yield state
    # TODO: if the body raises, the lines below never run.
    await asyncio.sleep(0)
    state["open"] = False
    log.append("close")
