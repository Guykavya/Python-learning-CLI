lo = int(input())
hi = int(input())

found = False
for x in range(lo, hi + 1):
    # count the digits (0 counts as one digit)
    k = 1
    t = x // 10
    while t > 0:
        k += 1
        t //= 10

    # add up each digit to the power k
    total = 0
    t = x
    while t > 0:
        total += (t % 10) ** k
        t //= 10

    if total == x:
        print(x)
        found = True

if not found:
    print("none")
