def solve_sudoku(board):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    empties = []
    for r in range(9):
        for c in range(9):
            d = board[r][c]
            if d == 0:
                empties.append((r, c))
                continue
            b = (r // 3) * 3 + c // 3
            if d in rows[r] or d in cols[c] or d in boxes[b]:
                return None
            rows[r].add(d); cols[c].add(d); boxes[b].add(d)

    def go(k):
        if k == len(empties):
            return True
        r, c = empties[k]
        b = (r // 3) * 3 + c // 3
        for d in range(1, 10):
            if d in rows[r] or d in cols[c] or d in boxes[b]:
                continue
            board[r][c] = d
            rows[r].add(d); cols[c].add(d); boxes[b].add(d)
            if go(k + 1):
                return True
            board[r][c] = 0
            rows[r].remove(d); cols[c].remove(d); boxes[b].remove(d)
        return False

    return board if go(0) else None
