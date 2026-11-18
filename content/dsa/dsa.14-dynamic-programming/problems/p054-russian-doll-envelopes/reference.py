from bisect import bisect_left


def max_envelopes(envelopes):
    order = sorted(envelopes, key=lambda e: (e[0], -e[1]))   # width up, height DOWN on ties
    tails = []
    for _, h in order:
        k = bisect_left(tails, h)            # strictly increasing heights
        if k == len(tails):
            tails.append(h)
        else:
            tails[k] = h
    return len(tails)
