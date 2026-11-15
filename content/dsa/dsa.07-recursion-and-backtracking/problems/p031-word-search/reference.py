def exist(board, word):
    rows, cols = len(board), len(board[0])

    def go(r, c, k):
        if k == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[k]:
            return False
        saved = board[r][c]
        board[r][c] = "#"
        found = (go(r + 1, c, k + 1) or go(r - 1, c, k + 1) or
                 go(r, c + 1, k + 1) or go(r, c - 1, k + 1))
        board[r][c] = saved
        return found

    return any(go(r, c, 0) for r in range(rows) for c in range(cols))
