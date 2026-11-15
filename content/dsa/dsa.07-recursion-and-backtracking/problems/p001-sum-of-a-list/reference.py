def total(xs, i=0):
    if i == len(xs):
        return 0
    return xs[i] + total(xs, i + 1)
