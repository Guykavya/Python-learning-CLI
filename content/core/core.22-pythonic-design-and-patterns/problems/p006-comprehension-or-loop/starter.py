def squares_of_evens(nums):
    """Squares of the even numbers, in order."""
    result = []
    for n in nums:
        if n % 2 == 0:
            result.append(n * n)
    return result


def word_lengths(text):
    """{word: length} for each word in text.split()."""
    lengths = {}
    for w in text.split():
        lengths[w] = len(w)
    return lengths


def count_long(words, n):
    """How many words are longer than n letters."""
    return len([w for w in words if len(w) > n])


def any_big(items, limit):
    """True if any item is greater than limit. Items may be a long or endless stream."""
    big = [x for x in items if x > limit]
    return len(big) > 0


def flatten(matrix):
    """[[1, 2], [3], []] -> [1, 2, 3]."""
    flat = []
    for row in matrix:
        for x in row:
            flat.append(x)
    return flat


def pythagorean_triples(n):
    """All (a, b, c) with 1 <= a < b < c <= n and a*a + b*b == c*c, in ascending order."""
    found = []
    for a in range(1, n + 1):
        for b in range(a + 1, n + 1):
            for c in range(b + 1, n + 1):
                if a * a + b * b == c * c:
                    found.append((a, b, c))
    return found


def log_and_double(items, log):
    """Call log(item) for every item, in order. Return the doubled items."""
    result = []
    for item in items:
        log(item)
        result.append(item * 2)
    return result


def first_duplicate(items):
    """The first item that appears a second time, or None. Stop reading as soon as you know."""
    seen = set()
    for item in items:
        if item in seen:
            return item
        seen.add(item)
    return None
