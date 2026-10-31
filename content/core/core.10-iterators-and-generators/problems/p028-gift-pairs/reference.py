from itertools import combinations


def gift_pairs(items, budget):
    return [
        (name1, name2)
        for (name1, price1), (name2, price2) in combinations(items, 2)
        if price1 + price2 == budget
    ]
