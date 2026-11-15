MOD = 10**9 + 7
n = int(input())

is_prime = bytearray([1]) * (n + 1)
is_prime[0] = 0
if n >= 1:
    is_prime[1] = 0
p = 2
while p * p <= n:
    if is_prime[p]:
        is_prime[p * p::p] = bytearray(len(range(p * p, n + 1, p)))
    p += 1

ans = 1
for p in range(2, n + 1):
    if is_prime[p]:
        pk = p
        while pk * p <= n:
            pk *= p
        ans = ans * pk % MOD
print(ans)
