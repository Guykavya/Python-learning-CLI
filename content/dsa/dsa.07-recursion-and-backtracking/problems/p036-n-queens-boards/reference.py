def solve_n_queens(n):
    solutions = []
    cols_of = []
    cols, diag, anti = set(), set(), set()

    def go(r):
        if r == n:
            solutions.append(["." * c + "Q" + "." * (n - c - 1) for c in cols_of])
            return
        for c in range(n):
            if c in cols or (r - c) in diag or (r + c) in anti:
                continue
            cols_of.append(c); cols.add(c); diag.add(r - c); anti.add(r + c)
            go(r + 1)
            cols_of.pop(); cols.remove(c); diag.remove(r - c); anti.remove(r + c)

    go(0)
    return solutions
