def capture(board):
    if not board:
        return []
    rows, cols = len(board), len(board[0])
    safe = [[False] * cols for _ in range(rows)]
    stack = []
    for r in range(rows):
        for c in range(cols):
            on_border = r == 0 or r == rows - 1 or c == 0 or c == cols - 1
            if on_border and board[r][c] == "O":
                safe[r][c] = True
                stack.append((r, c))
    while stack:
        r, c = stack.pop()
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == "O" and not safe[nr][nc]:
                safe[nr][nc] = True
                stack.append((nr, nc))
    return ["".join("O" if safe[r][c] else "X" for c in range(cols)) for r in range(rows)]
