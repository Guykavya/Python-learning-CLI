r, c = [int(x) for x in input().split()]
m = [[int(x) for x in input().split()] for _ in range(r)]
t = [[row[i] for row in m] for i in range(c)]
for row in t:
    print(" ".join(str(v) for v in row))
