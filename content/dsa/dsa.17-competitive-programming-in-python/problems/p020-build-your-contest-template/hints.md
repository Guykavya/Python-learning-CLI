## Hint 1

`Reader` is a list of tokens plus a position. Which methods of the standard library give you the tokens of a whole text in one call?

## Hint 2

For `make_ncr`, build the factorial list in one loop and the inverse factorials in a downward loop from one `pow(..., p - 2, p)` (problem p011). For `tree_depths`, copy your solution of p008 into a function.

## Hint 3

```text
Reader: self.t = text.split(); self.i = 0
  int(): v = int(self.t[self.i]); self.i += 1; return v
Out: self.lines = []; text(): "\n".join(lines) + "\n" if lines else ""
solve_cases: r = Reader(text); out = Out(); for _ in range(r.int()): out.add(solve(r)); return out.text()
main_from_stdin: sys.stdout.write(solve_cases(solve, sys.stdin.read()))
```
