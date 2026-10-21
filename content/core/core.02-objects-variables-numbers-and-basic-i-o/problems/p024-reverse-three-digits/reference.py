n = int(input())
hundreds = n // 100
tens = n // 10 % 10
ones = n % 10
rev = ones * 100 + tens * 10 + hundreds
print(rev)
print(abs(n - rev))
