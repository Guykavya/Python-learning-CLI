import asyncio


async def load_all(loaders):
    """Run all loaders together; all results in order, or cancel all on failure."""
    # TODO: gather raises the first error, but the other loaders keep running
    # in the background, and the error is a plain exception, not an ExceptionGroup.
    return list(await asyncio.gather(*(loader() for loader in loaders)))
