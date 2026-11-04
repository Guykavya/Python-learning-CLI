r, c, q = [int(x) for x in input().split()]
# TODO: mark each rectangle at its four corners in a difference grid, then take a 2D prefix sum once
for _ in range(q):
    r1, c1, r2, c2, v = [int(x) for x in input().split()]
for i in range(r):
    print(" ".join(["0"] * c))
