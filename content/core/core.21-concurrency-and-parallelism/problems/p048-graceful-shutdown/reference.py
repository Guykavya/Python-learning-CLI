import asyncio


class Service:
    """Runs `workers` background tasks that call `await job(worker_id)` forever."""

    def __init__(self, job, workers=2):
        self.job = job
        self.workers = workers
        self.log = []
        self._tasks = []

    @property
    def running(self):
        return bool(self._tasks)

    def start(self, n=None):
        if self._tasks:
            raise RuntimeError("service is already running")
        count = self.workers if n is None else n
        self._tasks = [
            asyncio.create_task(self._worker(i), name=f"worker-{i}") for i in range(count)
        ]

    async def _worker(self, worker_id):
        self.log.append(f"start {worker_id}")
        try:
            while True:
                await self.job(worker_id)
        finally:
            self.log.append(f"stop {worker_id}")    # runs once, however the worker ends

    async def stop(self):
        tasks, self._tasks = self._tasks, []        # a second stop() finds nothing to do
        for task in tasks:
            task.cancel()                           # no effect on tasks that already ended
        outcomes = await asyncio.gather(*tasks, return_exceptions=True)
        # CancelledError is a BaseException, not an Exception: only real crashes remain
        return [o for o in outcomes if isinstance(o, Exception)]

    async def __aenter__(self):
        self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.stop()
        return False
