import asyncio


async def handle_jobs(jobs, cpu_fn, executor):
    """Run cpu_fn(job) for each job on `executor`, concurrently; results in job order."""
    loop = asyncio.get_running_loop()
    futures = [loop.run_in_executor(executor, cpu_fn, job) for job in jobs]
    return await asyncio.gather(*futures)
