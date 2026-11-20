import sys


def prob_a(it):
    t = int(next(it))
    out = []
    for _ in range(t):
        s = next(it)
        out.append(str(sum(1 for i in range(1, len(s)) if s[i] == s[i - 1])))
    return out


def prob_b(it):
    t = int(next(it))
    out = []
    for _ in range(t):
        n = int(next(it))
        k = int(next(it))
        cnt = {}
        ans = 0
        for _ in range(n):
            x = int(next(it))
            ans += cnt.get(k - x, 0)
            cnt[x] = cnt.get(x, 0) + 1
        out.append(str(ans))
    return out


def prob_c(it):
    n = int(next(it))
    m = int(next(it))
    w = m + 2
    g = bytearray((n + 2) * w)
    for r in range(n):
        row = next(it)
        base = (r + 1) * w + 1
        for c, ch in enumerate(row):
            if ch == "#":
                g[base + c] = 1
    islands = 0
    for start in range(len(g)):
        if g[start]:
            islands += 1
            g[start] = 0
            stack = [start]
            while stack:
                u = stack.pop()
                for v in (u + 1, u - 1, u + w, u - w):
                    if g[v]:
                        g[v] = 0
                        stack.append(v)
    return [str(islands)]


def main():
    it = iter(sys.stdin.read().split())
    kind = next(it)
    f = {"A": prob_a, "B": prob_b, "C": prob_c}[kind]
    sys.stdout.write("\n".join(f(it)) + "\n")


main()
