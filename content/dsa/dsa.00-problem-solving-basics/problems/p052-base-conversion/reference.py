n = int(input())
b = int(input())

DIGITS = "0123456789ABCDEF"

if b < 2 or b > 16:
    print("invalid base")
elif n == 0:
    print("0")
else:
    sign = ""
    if n < 0:
        sign = "-"
    m = abs(n)
    result = ""
    while m > 0:
        # m % b is the LAST digit, so put it in front of what we have.
        result = DIGITS[m % b] + result
        m //= b
    print(sign + result)
