import math

x1 = float(input())
y1 = float(input())
x2 = float(input())
y2 = float(input())
dx = x2 - x1
dy = y2 - y1
print(f"Straight line: {math.hypot(dx, dy):.3f}")
print(f"City blocks: {abs(dx) + abs(dy):.3f}")
