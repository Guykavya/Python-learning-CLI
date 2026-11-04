import sys

q = int(sys.stdin.readline())
s = []
# TODO: write lower(x) and upper(x), then handle add / remove / count_le / kth / ceil
for _ in range(q):
    op, v = sys.stdin.readline().split()
    if op == "add":
        s.append(int(v))
    else:
        print("none")
