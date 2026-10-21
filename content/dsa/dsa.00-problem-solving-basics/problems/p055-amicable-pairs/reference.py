n = int(input())

found = False
for a in range(2, n + 1):
    # Sum of proper divisors of a: pair each divisor d <= sqrt(a) with a // d.
    s = 1
    d = 2
    while d * d <= a:
        if a % d == 0:
            s += d
            if d != a // d:
                s += a // d
        d += 1
    b = s
    if b > a and b <= n:
        # Now the sum of proper divisors of b must come back to a.
        t = 1
        d = 2
        while d * d <= b:
            if b % d == 0:
                t += d
                if d != b // d:
                    t += b // d
            d += 1
        if t == a:
            print(a, b)
            found = True
if not found:
    print("none")
