import sys

data = sys.stdin.read().split()
n = int(data[0])
for x in data[1:1 + n]:
    print(int(x) ** 2)
