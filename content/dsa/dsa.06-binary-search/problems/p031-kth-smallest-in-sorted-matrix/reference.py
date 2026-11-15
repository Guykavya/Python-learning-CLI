n, k = map(int, input().split())
m = [[int(x) for x in input().split()] for _ in range(n)]


def count_le(v):
    r, c, cnt = n - 1, 0, 0
    while r >= 0 and c < n:
        if m[r][c] <= v:
            cnt += r + 1
            c += 1
        else:
            r -= 1
    return cnt


lo, hi = m[0][0], m[n - 1][n - 1]
while lo < hi:
    mid = (lo + hi) // 2
    if count_le(mid) >= k:
        hi = mid
    else:
        lo = mid + 1
print(lo)
