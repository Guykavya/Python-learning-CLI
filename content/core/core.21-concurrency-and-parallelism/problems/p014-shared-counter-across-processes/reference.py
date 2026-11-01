from multiprocessing import Process, Value


def add_many(counter, times):
    """Add 1 to the shared counter `times` times. Runs in a child process."""
    for _ in range(times):
        with counter.get_lock():
            counter.value += 1


def count_in_processes(n_procs, per_proc):
    counter = Value("i", 0)
    procs = [Process(target=add_many, args=(counter, per_proc)) for _ in range(n_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    return counter.value


if __name__ == "__main__":
    print(count_in_processes(4, 1000))
