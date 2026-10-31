from itertools import islice


def grep(lines, word, max_count=None):
    target = word.lower()
    numbered = enumerate(lines, start=1)
    matches = ((n, line.rstrip()) for n, line in numbered if target in line.lower())
    yield from islice(matches, max_count)
