def min_paint_cost(costs):
    if not costs:
        return 0
    red, green, blue = costs[0]           # f[0][c]: house 0 painted colour c
    for c0, c1, c2 in costs[1:]:
        red, green, blue = (c0 + min(green, blue),
                            c1 + min(red, blue),
                            c2 + min(red, green))
    return min(red, green, blue)
