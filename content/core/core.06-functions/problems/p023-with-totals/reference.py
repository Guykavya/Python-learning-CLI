def with_totals(grid):
    """Return a new grid with a total at the end of each row and a final row of column totals."""
    if not grid:
        return []
    result = [row + [sum(row)] for row in grid]
    totals = [sum(r[j] for r in result) for j in range(len(result[0]))]
    result.append(totals)
    return result
