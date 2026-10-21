n = int(input())
if n < 0:
    print("no")
else:
    original = n
    rev = 0
    while n > 0:
        rev = rev * 10 + n % 10
        n //= 10
    if rev == original:
        print("yes")
    else:
        print("no")
