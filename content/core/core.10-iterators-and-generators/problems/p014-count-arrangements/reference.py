from itertools import combinations, permutations, product


def count_arrangements(items, k):
    return {
        "product": sum(1 for _ in product(items, repeat=k)),
        "permutations": sum(1 for _ in permutations(items, k)),
        "combinations": sum(1 for _ in combinations(items, k)),
    }
