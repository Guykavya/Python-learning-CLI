import threading


def run_in_threads(func, args_list):
    """Call func(*args) for every tuple in args_list, each in its own thread.

    Start all threads, then join all. Return the results in input order.
    """
    return []
