n = int(input())
balloons = []
for _ in range(n):
    xs, xe = map(int, input().split())
    balloons.append((xs, xe))
balloons.sort(key=lambda b: b[1])
arrows = 0
last = -10**18
for xs, xe in balloons:
    if xs > last:
        arrows += 1
        last = xe
print(arrows)
