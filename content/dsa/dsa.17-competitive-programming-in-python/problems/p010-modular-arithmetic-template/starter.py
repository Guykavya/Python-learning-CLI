import sys

data = sys.stdin.read().split()
t = int(data[0])
out = []
for i in range(t):
    a = int(data[1 + 3 * i])
    b = int(data[2 + 3 * i])
    p = int(data[3 + 3 * i])
    # TODO: a / b mod p, or -1 when b % p == 0
    out.append("0")
print("\n".join(out))
