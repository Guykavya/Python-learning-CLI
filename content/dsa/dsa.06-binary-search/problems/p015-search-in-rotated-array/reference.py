n = int(input())
a = [int(x) for x in input().split()]
q = int(input())
queries = [int(x) for x in input().split()]
out = []
for x in queries:
    lo, hi = 0, n - 1
    ans = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == x:
            ans = mid
            break
        if a[lo] <= a[mid]:
            if a[lo] <= x < a[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:
            if a[mid] < x <= a[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    out.append(ans)
print("\n".join(map(str, out)))
