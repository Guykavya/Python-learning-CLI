def total(numbers):
    result = 0
    for n in numbers:
        result += n
    return result


def longest(words):
    return max(words, key=len)


def price_of(menu, item):
    return menu[item]


def shout_all(words):
    return [w.upper() for w in words]


def centre(points):
    xs = sum(x for x, y in points) / len(points)
    ys = sum(y for x, y in points) / len(points)
    return xs, ys


def by_length(words):
    groups = {}
    for w in words:
        groups.setdefault(len(w), []).append(w)
    return groups
