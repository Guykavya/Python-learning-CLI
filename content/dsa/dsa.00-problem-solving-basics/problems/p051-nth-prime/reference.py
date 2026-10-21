k = int(input())

if k == 1:
    print(2)
else:
    count = 1        # 2 is already counted
    x = 1
    while count < k:
        x += 2       # only odd numbers can be primes now
        is_prime = True
        d = 3
        while d * d <= x:
            if x % d == 0:
                is_prime = False
                break
            d += 2
        if is_prime:
            count += 1
    print(x)
