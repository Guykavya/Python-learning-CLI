## Design

The program has three layers, and keeping them apart is what makes it manageable:

1. **Preprocessing, once:** read the log and build `P` with `P[i] = a[0] + ... + a[i-1]`.
2. **One function per command**, taking integers and returning the output string, including its own range check.
3. **A dispatcher** that turns a text line into a function call or `error`. A dictionary `name -> (argument count,
   function)` replaces a long `if` chain and makes "unknown name" and "wrong count" one check each.

| command | pattern | cost |
|---|---|---|
| `sum l r` | prefix sums | O(1) |
| `best k` | fixed window via `P[i + k] - P[i]` | O(n) |
| `above k t` | fixed window, compare the sum with `t * k` | O(n) |
| `maxsub b` | Kadane on `a[i] - b` | O(n) |
| `longest_le S` | variable window (valid because readings are >= 0) | O(n) |
| `maxwin k` | monotonic deque | O(n) |

## Code

```python
from collections import deque

n = int(input())
a = [int(x) for x in input().split()]

P = [0] * (n + 1)
for i in range(n):
    P[i + 1] = P[i] + a[i]


def is_int(s):
    digits = s[1:] if s.startswith("-") else s
    return digits.isdigit()


def cmd_sum(l, r):
    if not (1 <= l <= r <= n):
        return "error"
    return str(P[r] - P[l - 1])


def cmd_best(k):
    if not (1 <= k <= n):
        return "error"
    return str(max(P[i + k] - P[i] for i in range(n - k + 1)))


def cmd_maxsub(b):
    cur = best = a[0] - b
    for i in range(1, n):
        x = a[i] - b
        cur = cur + x if cur >= 0 else x
        if cur > best:
            best = cur
    return str(best)


def cmd_longest_le(S):
    left = 0
    total = 0
    best = 0
    for right in range(n):
        total += a[right]
        while total > S and left <= right:
            total -= a[left]
            left += 1
        if right - left + 1 > best:
            best = right - left + 1
    return str(best)


def cmd_above(k, t):
    if not (1 <= k <= n):
        return "error"
    need = t * k
    return str(sum(1 for i in range(n - k + 1) if P[i + k] - P[i] >= need))


def cmd_maxwin(k):
    if not (1 <= k <= n):
        return "error"
    dq = deque()
    out = []
    for i in range(n):
        while dq and a[dq[-1]] <= a[i]:
            dq.pop()
        dq.append(i)
        if dq[0] <= i - k:
            dq.popleft()
        if i >= k - 1:
            out.append(str(a[dq[0]]))
    return " ".join(out)


COMMANDS = {
    "sum": (2, cmd_sum),
    "best": (1, cmd_best),
    "maxsub": (1, cmd_maxsub),
    "longest_le": (1, cmd_longest_le),
    "above": (2, cmd_above),
    "maxwin": (1, cmd_maxwin),
}


def answer(line):
    parts = line.split()
    if not parts or parts[0] not in COMMANDS:
        return "error"
    count, func = COMMANDS[parts[0]]
    args = parts[1:]
    if len(args) != count or not all(is_int(x) for x in args):
        return "error"
    return func(*[int(x) for x in args])


q = int(input())
out = []
for _ in range(q):
    out.append(answer(input()))
print("\n".join(out))
```

## Details that matter

- **`longest_le` with a negative `S`.** The guard `left <= right` stops the shrinking at an empty window (sum 0). Without
  it, `total > S` stays true for `S < 0` and `left` runs off the end. The empty window has length 0, which is the right
  answer.
- **`above` without floats.** "average >= t" is "sum >= t * k" for a positive `k`; integer comparison is exact, a float
  average is not for big sums.
- **`maxsub` can be negative.** With `b = 100` every value is negative, and the best non-empty stretch is the largest
  single reading minus 100. Starting `best` at 0 would wrongly allow an empty stretch.
- **Validation order.** Check the name, then the count, then the integer format, and only then convert. Converting first
  crashes on `1.5`.
- **Output speed.** 200000 answers are collected and printed with one `join`.

## Complexity

O(n) to build `P`, O(1) per `sum`, O(n) per other command: with at most 20 heavy commands, about `20 n + q` steps.

## Another way

`best` and `above` can also slide a running window sum instead of using `P`. `maxsub` can be computed with prefix sums:
for each end, subtract the smallest earlier prefix of the shifted values. `longest_le` can use binary search: since
readings are non-negative, `P` never decreases, so for each end the earliest valid start is found with
`bisect_left(P, P[r] - S)`. Each of these is a good way to test your main version.
