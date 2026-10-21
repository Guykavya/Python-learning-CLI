n = int(input())

is_prime = n >= 2
d = 2
while is_prime and d * d <= n:
    if n % d == 0:
        is_prime = False
    d += 1

if is_prime:
    print("prime")
else:
    print("not prime")
