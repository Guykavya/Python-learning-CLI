import math

n = int(input())

# Count pairs (i, m) with i * m <= n. Every pair has i <= r or m <= r, where r = floor(sqrt(n)).
r = math.isqrt(n)
side = 0
for i in range(1, r + 1):
    side += n // i              # pairs with this i (any m)
# side counts the pairs with i <= r; by symmetry the same number has m <= r.
# Pairs with both i <= r and m <= r were counted twice: there are r * r of them.
print(2 * side - r * r)
