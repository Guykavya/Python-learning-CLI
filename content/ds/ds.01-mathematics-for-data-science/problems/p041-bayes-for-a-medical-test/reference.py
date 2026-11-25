def bayes_posterior(prior, sensitivity, false_positive_rate):
    tp = sensitivity * prior
    fp = false_positive_rate * (1 - prior)
    if tp + fp == 0:
        raise ValueError("no one can test positive: the posterior is undefined")
    return tp / (tp + fp)
