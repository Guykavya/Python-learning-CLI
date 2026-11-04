r, c = [int(x) for x in input().split()]
grid = [[int(x) for x in input().split()] for _ in range(r)]
q = int(input())
targets = [int(x) for x in input().split()]
# TODO: for each target start at the top-right corner; too big -> move left, too small -> move down
for x in targets:
    print("no")
