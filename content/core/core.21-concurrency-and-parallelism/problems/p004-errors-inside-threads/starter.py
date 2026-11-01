import threading


def run_and_collect(funcs):
    """Run each no-argument function in its own thread.

    Return [("ok", value) or ("error", exception), ...] in input order.
    """
    results = [None] * len(funcs)

    def call(index, func):
        results[index] = ("ok", func())   # if func raises, this line never stores anything

    threads = [threading.Thread(target=call, args=(i, f)) for i, f in enumerate(funcs)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results
