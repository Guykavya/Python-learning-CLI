import threading
import time


def worker(stop, tick, interval):
    """Call tick() every `interval` seconds until `stop` is set. Return the number of ticks."""
    count = 0
    while not stop.is_set():
        tick()
        count += 1
        time.sleep(interval)          # cannot be interrupted by stop.set()
    return count
