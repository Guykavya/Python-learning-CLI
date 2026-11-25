import statistics


def flag_iqr(values, k=1.5):
    if len(values) < 2:
        return []
    q1, _, q3 = statistics.quantiles(values, n=4, method="inclusive")
    iqr = q3 - q1
    low, high = q1 - k * iqr, q3 + k * iqr
    return [i for i, x in enumerate(values) if x < low or x > high]


def flag_z(values, t=3):
    if len(values) < 2:
        return []
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)
    if sd == 0:
        return []
    return [i for i, x in enumerate(values) if abs(x - mean) / sd > t]
