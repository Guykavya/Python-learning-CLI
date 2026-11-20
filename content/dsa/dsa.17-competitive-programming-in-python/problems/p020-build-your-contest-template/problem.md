# Build your contest template

Build the file you will paste at the start of a contest: the **template** of chapter section 12, as a small library in `solution.py`. The tests import your functions and use them to solve four earlier problems of this module on big inputs.

Write these (no input is read when the file is **imported**):

```python
class Reader:
    def __init__(self, text): ...
    def int(self): ...            # next token as int
    def ints(self, n): ...        # next n tokens as a list of ints
    def word(self): ...           # next token as a string
    def grid(self, n): ...        # next n tokens as a list of strings
    def has_more(self): ...       # True while tokens remain

class Out:
    def add(self, x): ...         # append str(x) as one line
    def text(self): ...           # all lines joined by "\n" plus a final "\n"; "" when empty

def solve_cases(solve, text): ...
    # Reader(text); t = r.int(); for each case out.add(solve(r)); return out.text()

def main_from_stdin(solve): ...
    # reads all of stdin once, calls solve_cases, writes the result with ONE write

def make_ncr(N, p): ...
    # returns f(n, r) = C(n, r) mod p for 0 <= n <= N (0 if r < 0 or r > n); p prime

def mod_div(a, b, p): ...
    # a / b mod p, or None if b % p == 0

def tree_depths(n, edges, root=1): ...
    # list d of length n + 1 with d[v] = depth of v (d[root] = 0), -1 for unreachable vertices and index 0;
    # iterative (no recursion)
```

`Reader` must split the text **once** and then only move an index; `has_more()` is `True` while tokens remain.

## Example

```python
from solution import Reader, solve_cases

def solve(r):
    n = r.int()
    return sum(r.ints(n))

print(solve_cases(solve, "2\n3\n1 2 3\n2\n10 20\n"), end="")
# 6
# 30
```
