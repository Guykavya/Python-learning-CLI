import sys

out = []
total = 0
for line in sys.stdin:
    s = sum(map(int, line.split()))
    out.append(str(s))
    total += s
out.append(f"total: {total}")
print("\n".join(out))
