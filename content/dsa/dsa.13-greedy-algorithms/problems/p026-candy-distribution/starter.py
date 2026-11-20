def min_candies(ratings):
    """Fewest candies: everyone >= 1, a higher rating than a neighbour means more candies than that neighbour."""
    c = [1] * len(ratings)
    for i in range(1, len(ratings)):
        if ratings[i] > ratings[i - 1]:
            c[i] = c[i - 1] + 1
    return sum(c)
