from itertools import cycle, islice


def cycle_labels(labels, n):
    return list(islice(cycle(labels), n))
