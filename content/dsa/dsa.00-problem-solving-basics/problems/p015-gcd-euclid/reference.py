a = abs(int(input()))
b = abs(int(input()))
while b != 0:
    a, b = b, a % b
print(a)
