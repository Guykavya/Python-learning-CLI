def ext(a, b):
    # return (g, x, y) with a*x + b*y = g = gcd(a, b), by the algorithm in problem.md
    return 0, 0, 0


q = int(input())
for _ in range(q):
    a, b = [int(x) for x in input().split()]
    g, x, y = ext(a, b)
    print(g, x, y)
