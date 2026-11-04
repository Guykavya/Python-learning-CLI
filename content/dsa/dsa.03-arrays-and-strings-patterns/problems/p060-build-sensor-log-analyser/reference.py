from collections import deque

n = int(input())
a = [int(x) for x in input().split()]

P = [0] * (n + 1)                      # P[i] = a[0] + ... + a[i-1]
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
    # Kadane on a[i] - b, at least one element
    cur = best = a[0] - b
    for i in range(1, n):
        x = a[i] - b
        cur = cur + x if cur >= 0 else x
        if cur > best:
            best = cur
    return str(best)


def cmd_longest_le(S):
    # readings are >= 0, so a variable window works
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
    need = t * k                       # average >= t  <=>  sum >= t * k (no floats)
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


COMMANDS = {               # name -> (number of arguments, function)
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
