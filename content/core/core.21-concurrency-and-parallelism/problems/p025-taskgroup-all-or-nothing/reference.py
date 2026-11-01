import asyncio


async def load_all(loaders):
    """Run all loaders together; all results in order, or cancel all on failure."""
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(loader()) for loader in loaders]
    return [task.result() for task in tasks]
