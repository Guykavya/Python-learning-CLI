n = int(input())
balloons = []
for _ in range(n):
    xs, xe = map(int, input().split())
    balloons.append((xs, xe))
# TODO: minimum number of arrows (closed intervals; touching balloons are burst together)
print(n)
