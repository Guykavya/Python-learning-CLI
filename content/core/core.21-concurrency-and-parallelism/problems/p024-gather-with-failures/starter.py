import asyncio


async def fetch_report(ids, fetch):
    """Return (ok, failed): id -> result, and id -> exception type name."""
    # TODO: one failure makes gather raise, and every result is lost.
    results = await asyncio.gather(*(fetch(i) for i in ids))
    return dict(zip(ids, results)), {}
