n = abs(int(input()))
total = n % 10 + n // 10 % 10 + n // 100 % 10 + n // 1000 % 10
print(total)
print(total % 3 == 0)
