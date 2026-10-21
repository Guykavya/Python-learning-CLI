n = int(input())

if n == 0:
    print("0")
else:
    result = ""
    while n > 0:
        result = str(n % 2) + result
        n //= 2
    print(result)
