import threading


def worker(stop, tick, interval):
    """Call tick() every `interval` seconds until `stop` is set. Return the number of ticks."""
    count = 0
    while not stop.is_set():
        tick()
        count += 1
        if stop.wait(interval):       # True as soon as stop is set, False after the timeout
            break
    return count
