import threading


def run_limited(funcs, limit):
    """Run every function in its own thread, at most `limit` at a time. Results in order."""
    results = [None] * len(funcs)
    places = threading.BoundedSemaphore(limit)

    def call(index, func):
        with places:                      # wait for a free place, give it back at the end
            results[index] = func()

    threads = [threading.Thread(target=call, args=(i, f)) for i, f in enumerate(funcs)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results
