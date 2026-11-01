from math import isqrt


def squares_of_evens(nums):
    return [n * n for n in nums if n % 2 == 0]


def word_lengths(text):
    return {w: len(w) for w in text.split()}


def count_long(words, n):
    return sum(1 for w in words if len(w) > n)


def any_big(items, limit):
    return any(x > limit for x in items)


def flatten(matrix):
    return [x for row in matrix for x in row]


def pythagorean_triples(n):
    return [
        (a, b, isqrt(a * a + b * b))
        for a in range(1, n + 1)
        for b in range(a + 1, n + 1)
        if isqrt(a * a + b * b) <= n and isqrt(a * a + b * b) ** 2 == a * a + b * b
    ]


def log_and_double(items, log):
    result = []
    for item in items:
        log(item)
        result.append(item * 2)
    return result


def first_duplicate(items):
    seen = set()
    for item in items:
        if item in seen:
            return item
        seen.add(item)
    return None
