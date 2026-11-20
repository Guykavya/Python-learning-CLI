import sys

it = iter(sys.stdin.read().split())
t = int(next(it))
out = []
for _ in range(t):
    # TODO: read n, then n numbers; count those above the average
    out.append("0")
print("\n".join(out))
