# This program has bugs. Find them with small tests and dry runs, then fix it.
# Count the primes x with a <= x <= b.
a = int(input())
b = int(input())
count = 0
is_prime = True
for x in range(a, b):
    d = 2
    while d * d < x:
        if x % d == 0:
            is_prime = False
            break
        d += 1
    if is_prime:
        count += 1
print(count)
