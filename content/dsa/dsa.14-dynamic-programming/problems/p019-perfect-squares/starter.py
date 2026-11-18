def num_squares(n):
    """Fewest perfect squares (1, 4, 9, ...) that add up to n."""
    count = 0
    k = 1
    while (k + 1) * (k + 1) <= n:
        k += 1
    while n > 0:                     # greedy: the biggest square that fits
        while k * k > n:
            k -= 1
        n -= k * k
        count += 1
    return count
