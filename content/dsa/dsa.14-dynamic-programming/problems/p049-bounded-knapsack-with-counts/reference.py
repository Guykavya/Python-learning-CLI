def bounded_knapsack(items, W):
    g = [0] * (W + 1)
    for weight, value, count in items:
        b = 1
        while count > 0:                     # bundles 1, 2, 4, ... and the rest
            take = min(b, count)
            bw, bv = take * weight, take * value
            for w in range(W, bw - 1, -1):   # each bundle is a 0/1 item: downwards
                cand = g[w - bw] + bv
                if cand > g[w]:
                    g[w] = cand
            count -= take
            b *= 2
    return g[W]
