n = int(input())
print((n & (n - 1)) == 0)
print(n.bit_length())
print(1 << (n.bit_length() - 1))
