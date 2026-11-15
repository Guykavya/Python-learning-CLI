n = int(input())
is_prime = [True] * (n + 1)
is_prime[0] = False
if n >= 1:
    is_prime[1] = False
p = 2
while p * p <= n:
    if is_prime[p]:
        for m in range(p * p, n + 1, p):
            is_prime[m] = False
    p += 1
print(" ".join(str(k) for k in range(2, n + 1) if is_prime[k]))
