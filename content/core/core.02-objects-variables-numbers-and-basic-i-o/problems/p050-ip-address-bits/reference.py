a = int(input())
b = int(input())
c = int(input())
d = int(input())
x = int(input())
n = (a << 24) | (b << 16) | (c << 8) | d
print("Integer:", n)
print("Hex:", hex(n))
print(f"Address: {x >> 24 & 255}.{x >> 16 & 255}.{x >> 8 & 255}.{x & 255}")
