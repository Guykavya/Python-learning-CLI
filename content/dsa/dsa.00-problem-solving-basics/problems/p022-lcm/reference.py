a = int(input())
b = int(input())

x = a
y = b
while y != 0:
    x, y = y, x % y
g = x

print(a // g * b)
