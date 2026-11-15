l, r = [int(x) for x in input().split()]

# base primes up to sqrt(r), by an ordinary sieve
limit = 1
while limit * limit <= r:
    limit += 1
small = [True] * (limit + 1)
base = []
for i in range(2, limit + 1):
    if small[i]:
        base.append(i)
        for m in range(i * i, limit + 1, i):
            small[m] = False

# segment: index j stands for the number l + j
size = r - l + 1
seg = bytearray([1]) * size
for p in base:
    if p * p > r:
        break
    start = max(p * p, (l + p - 1) // p * p)
    for m in range(start, r + 1, p):
        seg[m - l] = 0
if l <= 1:
    for v in range(l, min(r, 1) + 1):
        seg[v - l] = 0

count = 0
total = 0
for j in range(size):
    if seg[j]:
        count += 1
        total += l + j
print(count)
print(total)
