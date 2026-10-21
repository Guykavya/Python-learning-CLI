import math

x1 = float(input())
y1 = float(input())
x2 = float(input())
y2 = float(input())
print(f"Straight line: {math.sqrt((x2 - x1) + (y2 - y1)) ** 2:.3f}")
print(f"City blocks: {(x2 - x1) + (y2 - y1):.3f}")
