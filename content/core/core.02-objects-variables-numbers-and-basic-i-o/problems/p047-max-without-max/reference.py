a = int(input())
b = int(input())
c = int(input())
big = (a + b + abs(a - b)) // 2
small = (a + b - abs(a - b)) // 2
print(big)
print(small)
print((big + c + abs(big - c)) // 2)
