import sys

data = sys.stdin.read().split()
q = int(data[0])
queries = [int(x) for x in data[1:1 + q]]
top = max(queries)

is_prime = bytearray([1]) * (top + 1)
is_prime[0] = 0
if top >= 1:
    is_prime[1] = 0
p = 2
while p * p <= top:
    if is_prime[p]:
        is_prime[p * p::p] = bytearray(len(range(p * p, top + 1, p)))
    p += 1

count = [0] * (top + 1)
running = 0
for k in range(top + 1):
    running += is_prime[k]
    count[k] = running

print("\n".join(str(count[n]) for n in queries))
