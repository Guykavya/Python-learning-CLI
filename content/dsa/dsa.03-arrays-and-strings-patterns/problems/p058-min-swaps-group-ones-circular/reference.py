n = int(input())
a = [int(x) for x in input().split()]

m = sum(a)              # number of ones = size of the final block
if m == 0:
    print(0)
else:
    window = sum(a[:m])                 # ones in the window a[0..m-1]
    best = window
    for i in range(m, n + m - 1):       # the window ends at i % n; it starts at (i - m + 1) % n
        window += a[i % n] - a[(i - m) % n]
        if window > best:
            best = window
    print(m - best)
