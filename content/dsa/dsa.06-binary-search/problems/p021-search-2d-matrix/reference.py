r, c = map(int, input().split())
m = [[int(x) for x in input().split()] for _ in range(r)]
q = int(input())
queries = [int(x) for x in input().split()]
out = []
for x in queries:
    lo, hi = 0, r * c - 1
    ans = "-1 -1"
    while lo <= hi:
        mid = (lo + hi) // 2
        v = m[mid // c][mid % c]
        if v == x:
            ans = f"{mid // c} {mid % c}"
            break
        elif v < x:
            lo = mid + 1
        else:
            hi = mid - 1
    out.append(ans)
print("\n".join(out))
