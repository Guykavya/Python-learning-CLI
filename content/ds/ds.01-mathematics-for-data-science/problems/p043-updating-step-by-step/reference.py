def sequential_posterior(prior, results, sensitivity=0.99, false_positive_rate=0.05):
    p = prior
    for positive in results:
        if positive:
            num = sensitivity * p
            den = num + false_positive_rate * (1 - p)
        else:
            num = (1 - sensitivity) * p
            den = num + (1 - false_positive_rate) * (1 - p)
        p = num / den
    return p
