import asyncio


async def handle_jobs(jobs, cpu_fn, executor):
    """Run cpu_fn(job) for each job on `executor`, concurrently; results in job order."""
    results = []
    for job in jobs:
        results.append(cpu_fn(job))   # BUG: blocks the event loop, one job at a time
    return results
