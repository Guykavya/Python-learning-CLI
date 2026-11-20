import sys

it = iter(sys.stdin.read().split())
t = int(next(it))
out = []
for _ in range(t):
    n = int(next(it))
    a = [int(next(it)) for _ in range(n)]
    total = sum(a)
    out.append(str(sum(1 for x in a if x * n > total)))
print("\n".join(out))
