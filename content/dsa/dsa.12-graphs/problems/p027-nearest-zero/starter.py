from collections import deque


def nearest_zero(mat):
    """A new matrix with the distance from each cell to the nearest 0."""
    return [row[:] for row in mat]
