import statistics


def summary(data: list[float]) -> dict[str, object]:
    if not data:
        raise ValueError("summary() needs at least one value")
    return {
        "count": len(data),
        "mean": statistics.fmean(data),
        "median": statistics.median(data),
        "modes": statistics.multimode(data),
        "stdev": statistics.stdev(data) if len(data) >= 2 else None,
        "pstdev": statistics.pstdev(data),
        "range": max(data) - min(data),
    }


def quartiles(data: list[float]) -> list[float]:
    return statistics.quantiles(data, n=4)


def outliers(data: list[float]) -> list[float]:
    q1, _, q3 = quartiles(data)
    spread = q3 - q1
    low, high = q1 - 1.5 * spread, q3 + 1.5 * spread
    return [x for x in data if x < low or x > high]
