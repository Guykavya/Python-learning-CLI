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
        raise NotImplementedError("create one task per worker with asyncio.create_task")

    async def _worker(self, worker_id):
        raise NotImplementedError("log start; loop forever on job; log stop in finally")

    async def stop(self):
        raise NotImplementedError("cancel, wait for all, collect real errors, forget the tasks")

    async def __aenter__(self):
        self.start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.stop()
        return False
