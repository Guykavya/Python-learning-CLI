STRAIGHT = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIAGONAL = [(-1, -1), (-1, 1), (1, -1), (1, 1)]


def neighbours(grid, r, c, diagonal=False):
    rows, cols = len(grid), len(grid[0])
    moves = STRAIGHT + DIAGONAL if diagonal else STRAIGHT
    out = []
    for dr, dc in moves:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#":
            out.append((nr, nc))
    return out
