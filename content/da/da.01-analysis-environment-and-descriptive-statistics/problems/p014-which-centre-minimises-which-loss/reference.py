def total_loss(values, c, kind):
    if kind == "squared":
        return sum((x - c) ** 2 for x in values)
    if kind == "absolute":
        return sum(abs(x - c) for x in values)
    raise ValueError(f"unknown loss kind: {kind!r}")


def best_centre(values, kind):
    if not values:
        raise ValueError("empty list")
    mean = sum(values) / len(values)
    candidates = sorted(set(values) | {mean})
    return min(candidates, key=lambda c: total_loss(values, c, kind))
