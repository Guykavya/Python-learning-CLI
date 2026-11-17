import heapq
import itertools


class LazyPQ:
    """A priority queue with changes and removals. Smaller priority comes out first."""

    def __init__(self):
        pass

    def add(self, task, priority):
        """Add the task, or change its priority if it is already in the queue."""
        pass

    def remove(self, task):
        """Cancel the task. KeyError if it is not in the queue."""
        pass

    def pop(self):
        """Remove and return the task with the smallest priority. KeyError if the queue is empty."""
        return None

    def __len__(self):
        return 0

    def __contains__(self, task):
        return False

    def stored(self):
        """The number of entries in the heap list, stale ones included."""
        return 0
