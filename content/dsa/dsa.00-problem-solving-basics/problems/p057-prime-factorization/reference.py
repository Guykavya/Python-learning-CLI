n = int(input())

m = n               # what is left to factor
result = ""
d = 2
while d * d <= m:
    if m % d == 0:
        e = 0
        while m % d == 0:
            m //= d
            e += 1
        if result != "":
            result += " * "
        if e == 1:
            result += f"{d}"
        else:
            result += f"{d}^{e}"
    d += 1
if m > 1:
    # No divisor up to sqrt(m) is left, so m itself is prime.
    if result != "":
        result += " * "
    result += f"{m}"
print(f"{n} = {result}")
