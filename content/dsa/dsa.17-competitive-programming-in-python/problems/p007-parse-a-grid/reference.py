import sys

data = sys.stdin.read().split()
n, m = int(data[0]), int(data[1])
rows = data[2:2 + n]
sr = sc = er = ec = 0
walls = 0
for r, row in enumerate(rows, 1):
    walls += row.count("#")
    c = row.find("S")
    if c != -1:
        sr, sc = r, c + 1
    c = row.find("E")
    if c != -1:
        er, ec = r, c + 1
print(sr, sc, er, ec, walls)
