from itertools import islice


def first_lines(path, n):
    with open(path, encoding="utf-8") as f:
        return [line.rstrip("\n") for line in islice(f, n)]
