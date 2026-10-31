import statistics


def summary(data: list[float]) -> dict[str, object]:
    """count, mean, median, modes, stdev (sample, None for one value), pstdev, range."""
    return {}


def quartiles(data: list[float]) -> list[float]:
    """[Q1, Q2, Q3] using statistics.quantiles (default method)."""
    return []


def outliers(data: list[float]) -> list[float]:
    """Values more than 1.5 * IQR below Q1 or above Q3, in their original order."""
    return []
