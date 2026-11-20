def find_words(board, words):
    """Sorted list of the distinct words that can be traced on the board."""
    rows, cols = len(board), len(board[0])

    def trace(word, r, c, k, used):
        if board[r][c] != word[k] or (r, c) in used:
            return False
        if k == len(word) - 1:
            return True
        used.add((r, c))
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and trace(word, nr, nc, k + 1, used):
                used.discard((r, c))
                return True
        used.discard((r, c))
        return False

    found = set()
    for w in words:                   # one search per word: correct, but far too slow on the big tests
        if any(trace(w, r, c, 0, set()) for r in range(rows) for c in range(cols)):
            found.add(w)
    return sorted(found)
