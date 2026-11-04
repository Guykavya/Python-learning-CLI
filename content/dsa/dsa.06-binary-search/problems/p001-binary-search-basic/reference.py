n = int(input())
a = [int(x) for x in input().split()]
q = int(input())
targets = [int(x) for x in input().split()]
out = []
for x in targets:
    lo, hi = 0, n - 1
    ans = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == x:
            ans = mid
            break
        elif a[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    out.append(ans)
print("\n".join(map(str, out)))
