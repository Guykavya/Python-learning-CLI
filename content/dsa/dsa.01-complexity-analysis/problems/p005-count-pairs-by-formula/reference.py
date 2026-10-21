n = int(input())
# The inner loop runs n-1, n-2, ..., 1, 0 times: the sum 0 + 1 + ... + (n - 1).
print(n * (n - 1) // 2)
