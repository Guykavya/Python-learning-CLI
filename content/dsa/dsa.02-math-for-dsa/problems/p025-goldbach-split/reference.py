LIMIT = 10 ** 6
is_prime = [True] * (LIMIT + 1)
is_prime[0] = is_prime[1] = False
for i in range(2, LIMIT + 1):
    if i * i > LIMIT:
        break
    if is_prime[i]:
        for m in range(i * i, LIMIT + 1, i):
            is_prime[m] = False

k = int(input())
for _ in range(k):
    n = int(input())
    p = 2
    while not (is_prime[p] and is_prime[n - p]):
        p += 1
    print(p, n - p)
