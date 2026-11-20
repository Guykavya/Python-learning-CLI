## Approach

```python
import sys


class Reader:
    def __init__(self, text):
        self.tokens = text.split()
        self.pos = 0

    def int(self):
        v = int(self.tokens[self.pos])
        self.pos += 1
        return v

    def ints(self, n):
        v = list(map(int, self.tokens[self.pos:self.pos + n]))
        self.pos += n
        return v

    def word(self):
        v = self.tokens[self.pos]
        self.pos += 1
        return v

    def grid(self, n):
        v = self.tokens[self.pos:self.pos + n]
        self.pos += n
        return v

    def has_more(self):
        return self.pos < len(self.tokens)


class Out:
    def __init__(self):
        self.lines = []

    def add(self, x):
        self.lines.append(str(x))

    def text(self):
        return "\n".join(self.lines) + "\n" if self.lines else ""


def solve_cases(solve, text):
    r = Reader(text)
    out = Out()
    for _ in range(r.int()):
        out.add(solve(r))
    return out.text()


def main_from_stdin(solve):
    sys.stdout.write(solve_cases(solve, sys.stdin.read()))


def make_ncr(N, p):
    fact = [1] * (N + 1)
    for i in range(1, N + 1):
        fact[i] = fact[i - 1] * i % p
    inv = [1] * (N + 1)
    inv[N] = pow(fact[N], p - 2, p)
    for i in range(N, 0, -1):
        inv[i - 1] = inv[i] * i % p

    def ncr(n, r):
        if r < 0 or r > n:
            return 0
        return fact[n] * inv[r] % p * inv[n - r] % p

    return ncr


def mod_div(a, b, p):
    if b % p == 0:
        return None
    return a % p * pow(b, p - 2, p) % p


def tree_depths(n, edges, root=1):
    adj = [[] for _ in range(n + 1)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    d = [-1] * (n + 1)
    d[root] = 0
    stack = [root]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if d[v] == -1:
                d[v] = d[u] + 1
                stack.append(v)
    return d
```

The file is the sum of six pieces you already wrote in earlier problems (reading in p002 and p005, output in p004, `nCr` in p011, modular division in p010, iterative DFS in p008). The point of the exercise is to put them in one place with the same shape every time.

Example: `solve_cases(solve, "2\n3\n1 2 3\n2\n10 20\n")` reads `t = 2`, calls `solve` twice, and returns `"6\n30\n"`.

## Complexity

All helpers are linear in their input, except `make_ncr`, which is `O(N)` to build and `O(1)` per query.

## Another way

Keep one file per kind of problem (`graph.py`, `number_theory.py`) and merge before the contest. For contests you must paste one file, so one library file with sections is easier.
