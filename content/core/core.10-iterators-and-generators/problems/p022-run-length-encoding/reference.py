from itertools import groupby


def encode(text):
    return [(char, sum(1 for _ in group)) for char, group in groupby(text)]


def decode(pairs):
    return "".join(char * count for char, count in pairs)
