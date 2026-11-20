# Trace the template

This is the contest template of chapter section 12, with two extra `print` calls added for debugging. It is run with the input below. Predict **exactly** what it prints, line by line. Do not run it.

```python
import sys

def solve(it):
    n = int(next(it))
    a = [int(next(it)) for _ in range(n)]
    print("solving", n)
    best = a[0]
    for x in a:
        if x > best:
            best = x
    return f"{best} {a.index(best)}"

def main():
    it = iter(sys.stdin.read().split())
    t = int(next(it))
    out = []
    for case in range(1, t + 1):
        out.append(f"Case {case}: " + solve(it))
        if case == 2:
            print("two done")
    sys.stdout.write("\n".join(out) + "\n")
    print("end")

main()
```

Input:

```text
3
3
4 9 2
1
7
4
5 5 8 8
```

Write your answer in `answer.txt`, one printed line per line.

## How to work

1. List the tokens: `3 | 3 4 9 2 | 1 7 | 4 5 5 8 8`. The first `3` is `t`.
2. Go through the three cases in order. For each, note what `solve` **prints at once** (`solving n`) and what it **returns** (a string that goes into `out` and is not printed yet).
3. Remember when `"two done"` is printed (after case 2) and when the collected `out` is written (after the loop).
4. `a.index(best)` gives the position of the **first** occurrence of the maximum.

## After you answer

1. Why do the `solving ...` lines come **before** every `Case ...` line?
2. What would change if `solve` printed its result instead of returning it?
3. Where would `two done` appear if you moved the `print("two done")` line after the `for` loop?
