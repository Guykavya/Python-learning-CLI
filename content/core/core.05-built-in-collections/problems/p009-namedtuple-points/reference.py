from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
n = int(input())
points = []
for _ in range(n):
    x, y = [int(v) for v in input().split()]
    points.append(Point(x, y))
best = points[0]
for p in points:
    if p.x * p.x + p.y * p.y > best.x * best.x + best.y * best.y:
        best = p
print("Points:", len(points))
print("Farthest:", best)
print("Moved:", best._replace(x=best.x + 1))
print("Sum of x:", sum(p.x for p in points))
