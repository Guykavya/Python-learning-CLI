import sys

data = sys.stdin.read().split()
q = int(data[0])
queries = [int(x) for x in data[1:1 + q]]
top = max(queries)

spf = list(range(top + 1))
i = 2
while i * i <= top:
    if spf[i] == i:
        for m in range(i * i, top + 1, i):
            if spf[m] == m:
                spf[m] = i
    i += 1

out = []
for n in queries:
    ans = 1
    while n > 1:
        p = spf[n]
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        ans *= e + 1
    out.append(ans)
print("\n".join(map(str, out)))
