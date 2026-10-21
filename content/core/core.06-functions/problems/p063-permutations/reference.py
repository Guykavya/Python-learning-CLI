def permutations(items):
    """Return every ordering of items (as lists), first-item-first order. Recursive."""
    if not items:
        return [[]]
    result = []
    for i in range(len(items)):
        rest = items[:i] + items[i + 1:]
        for p in permutations(rest):
            result.append([items[i]] + p)
    return result


def anagrams(word):
    """Return the sorted list of distinct rearrangements of word."""
    return sorted({"".join(p) for p in permutations(list(word))})
