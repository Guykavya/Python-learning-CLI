import queue
import threading

_STOP = None          # sentinel: "no more jobs"


def pipeline(items, work, n_workers):
    """Process items with n_workers threads fed by a queue. Results in input order."""
    jobs = queue.Queue()
    results = [None] * len(items)

    def consumer():
        while True:
            job = jobs.get()
            if job is _STOP:
                break
            index, item = job
            results[index] = work(item)

    workers = [threading.Thread(target=consumer) for _ in range(n_workers)]
    for w in workers:
        w.start()
    for job in enumerate(items):          # producer
        jobs.put(job)
    for _ in workers:                     # one sentinel per worker
        jobs.put(_STOP)
    for w in workers:
        w.join()
    return results
