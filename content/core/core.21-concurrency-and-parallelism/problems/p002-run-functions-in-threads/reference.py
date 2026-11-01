import threading


def run_in_threads(func, args_list):
    """Call func(*args) for every tuple in args_list, each in its own thread.

    Start all threads, then join all. Return the results in input order.
    """
    results = [None] * len(args_list)

    def call(index, args):
        results[index] = func(*args)

    threads = [
        threading.Thread(target=call, args=(i, args))
        for i, args in enumerate(args_list)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results
