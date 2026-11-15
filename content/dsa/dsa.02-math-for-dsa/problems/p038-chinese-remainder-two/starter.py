q = int(input())
for _ in range(q):
    a1, m1, a2, m2 = [int(x) for x in input().split()]
    # smallest x >= 0 with x = a1 (mod m1) and x = a2 (mod m2), or -1
    print(-1)
