# Count the primes x with a <= x <= b.
a = int(input())
b = int(input())
count = 0
for x in range(a, b + 1):
    is_prime = x >= 2
    d = 2
    while d * d <= x:
        if x % d == 0:
            is_prime = False
            break
        d += 1
    if is_prime:
        count += 1
print(count)
