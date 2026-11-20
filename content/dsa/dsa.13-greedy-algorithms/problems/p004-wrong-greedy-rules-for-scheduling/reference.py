def wrong_rule_inputs():
    """Return (a, b): earliest start loses on a, shortest first loses on b."""
    # a: one long event starts first and covers three short ones (greedy 1 or 2, best 4)
    a = [(0, 20), (2, 4), (5, 7), (8, 10), (11, 13)]
    # b: two short events each sit across a pair of longer ones (greedy 2, best 4)
    b = [(0, 6), (7, 13), (14, 20), (21, 27), (5, 8), (19, 22)]
    return a, b
