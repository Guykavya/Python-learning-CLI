from multiprocessing import Process, Value

count = 0


def add_many(times):
    global count
    for _ in range(times):
        count += 1               # changes THIS process's copy only


def count_in_processes(n_procs, per_proc):
    procs = [Process(target=add_many, args=(per_proc,)) for _ in range(n_procs)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    return count                 # the parent's copy: still 0


if __name__ == "__main__":
    print(count_in_processes(4, 1000))
