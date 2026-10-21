n = int(input())

# The numbers from low = 2^(k-1) to 2^k - 1 all need exactly k doubling steps.
count = 0
k = 1
low = 1
while low <= n:
    high = min(n, 2 * low - 1)          # the last number in this group, but not past n
    count += k * (high - low + 1)
    low = low * 2
    k += 1
print(count)
