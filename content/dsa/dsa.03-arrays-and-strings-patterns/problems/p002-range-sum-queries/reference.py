n = int(input())
a = [int(x) for x in input().split()]

p = [0]
for x in a:
    p.append(p[-1] + x)

q = int(input())
out = []
for _ in range(q):
    l, r = map(int, input().split())
    out.append(p[r] - p[l - 1])

print("\n".join(map(str, out)))
