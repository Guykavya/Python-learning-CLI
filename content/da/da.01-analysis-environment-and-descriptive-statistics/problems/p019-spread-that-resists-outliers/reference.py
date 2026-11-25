import statistics


def describe_spread(values):
    if len(values) < 2:
        raise ValueError("need at least two values")
    s = sorted(values)
    q1, _, q3 = statistics.quantiles(s, n=4, method="inclusive")
    median = statistics.median(s)
    mean = statistics.fmean(s)
    sd = statistics.stdev(s)
    return {
        "range": s[-1] - s[0],
        "sd": sd,
        "iqr": q3 - q1,
        "mad": statistics.median(abs(x - median) for x in s),
        "cv": sd / mean if mean != 0 else None,
    }
