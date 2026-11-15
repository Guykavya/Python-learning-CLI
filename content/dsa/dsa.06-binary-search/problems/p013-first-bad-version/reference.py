n = int(input())
lo, hi = 1, n
while lo < hi:
    mid = (lo + hi) // 2
    print("?", mid, flush=True)
    if int(input()) == 1:
        hi = mid
    else:
        lo = mid + 1
print("!", lo, flush=True)
