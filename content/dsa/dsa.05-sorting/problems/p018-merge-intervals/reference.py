n = int(input())
intervals = []
for _ in range(n):
    l, r = map(int, input().split())
    intervals.append((l, r))
intervals.sort()
cl, cr = intervals[0]
out = []
for l, r in intervals[1:]:
    if l <= cr:
        cr = max(cr, r)
    else:
        out.append((cl, cr))
        cl, cr = l, r
out.append((cl, cr))
for l, r in out:
    print(l, r)
