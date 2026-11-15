import sys

q = int(sys.stdin.readline())
times = {}
vals = {}
out = []
for _ in range(q):
    parts = sys.stdin.readline().split()
    if parts[0] == "set":
        key, value, t = parts[1], parts[2], int(parts[3])
        times.setdefault(key, []).append(t)
        vals.setdefault(key, []).append(value)
    else:
        key, t = parts[1], int(parts[2])
        ts = times.get(key, [])
        lo, hi = 0, len(ts)
        while lo < hi:
            mid = (lo + hi) // 2
            if ts[mid] <= t:
                lo = mid + 1
            else:
                hi = mid
        out.append(vals[key][lo - 1] if lo > 0 else "NONE")
print("\n".join(out))
