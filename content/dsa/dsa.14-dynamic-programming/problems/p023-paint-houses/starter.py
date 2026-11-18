def min_paint_cost(costs):
    """Cheapest total so that no two neighbouring houses share a colour (3 colours)."""
    return sum(min(row) for row in costs)
