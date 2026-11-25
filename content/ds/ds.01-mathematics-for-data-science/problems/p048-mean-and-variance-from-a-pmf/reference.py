def mean_var(values, probs):
    if len(values) != len(probs):
        raise ValueError("values and probs must have the same length")
    if any(p < 0 for p in probs):
        raise ValueError("probabilities cannot be negative")
    if abs(sum(probs) - 1.0) > 1e-9:
        raise ValueError("probabilities must add up to 1")
    mean = sum(x * p for x, p in zip(values, probs))
    var = sum((x - mean) ** 2 * p for x, p in zip(values, probs))
    return mean, var
