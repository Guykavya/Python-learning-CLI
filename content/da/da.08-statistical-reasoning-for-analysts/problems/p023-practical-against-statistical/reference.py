def classify(lo, hi, mei=0.5):
    if lo > mei:
        label = "worth it: the whole interval is above the minimum effect"
    elif hi < mei:
        label = "not worth it: the whole interval is below the minimum effect"
    else:
        label = "inconclusive: the interval contains the minimum effect"
    return label, bool(lo > 0 or hi < 0)
