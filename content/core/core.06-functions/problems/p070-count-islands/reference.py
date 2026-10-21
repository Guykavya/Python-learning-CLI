def fill(grid, r, c, seen):
    """Mark the island through (r, c) as seen and return its size (0 if not unseen land)."""
    if r < 0 or r >= len(grid) or c < 0 or c >= len(grid[r]):
        return 0
    if grid[r][c] != "#" or (r, c) in seen:
        return 0
    seen.add((r, c))
    return (1 + fill(grid, r + 1, c, seen) + fill(grid, r - 1, c, seen)
            + fill(grid, r, c + 1, seen) + fill(grid, r, c - 1, seen))


def island_sizes(grid):
    """Return the sizes of the islands of '#' cells (4-directional), largest first."""
    seen = set()
    sizes = []
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == "#" and (r, c) not in seen:
                sizes.append(fill(grid, r, c, seen))
    return sorted(sizes, reverse=True)


def count_islands(grid):
    """Return the number of islands in grid."""
    return len(island_sizes(grid))
