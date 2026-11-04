import sys

data = sys.stdin.read().split()
q = int(data[0])
out = []
for token in data[1:1 + q]:
    n = int(token)
    count = 0
    while n:
        n &= n - 1
        count += 1
    out.append(count)
print("\n".join(map(str, out)))
