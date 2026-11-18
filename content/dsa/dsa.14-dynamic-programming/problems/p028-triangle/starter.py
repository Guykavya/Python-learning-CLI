def min_triangle_path(triangle):
    """Smallest top-to-bottom path sum; from position j you go to j or j + 1 in the next row."""
    return sum(min(row) for row in triangle)
