import asyncio


async def fetch_report(ids, fetch):
    """Return (ok, failed): id -> result, and id -> exception type name."""
    results = await asyncio.gather(*(fetch(i) for i in ids), return_exceptions=True)
    ok, failed = {}, {}
    for item_id, result in zip(ids, results):
        if isinstance(result, BaseException):
            failed[item_id] = type(result).__name__
        else:
            ok[item_id] = result
    return ok, failed
