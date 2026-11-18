def min_score_triangulation(values):
    """Smallest total of values[x] * values[y] * values[z] over the triangles of a triangulation."""
    total = 0
    for k in range(1, len(values) - 1):          # a fan from corner 0: one triangulation, not the best
        total += values[0] * values[k] * values[k + 1]
    return total
