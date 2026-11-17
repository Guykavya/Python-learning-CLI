from collections import deque

MOD = 10**9 + 7


def longest_from(n, edges, source):
    """best[v] = largest path weight from source to v, None if unreachable."""
    return [None] * n


def count_paths(n, edges, source, target):
    """Number of different paths from source to target, modulo 10**9 + 7."""
    return 0
