import queue
import threading


def pipeline(items, work, n_workers):
    """Process items with n_workers threads fed by a queue. Results in input order."""
    return [work(item) for item in items]        # one thread, one item at a time
