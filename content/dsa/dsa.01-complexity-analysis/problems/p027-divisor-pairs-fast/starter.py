n = int(input())

# Correct but slow: O(n log n). Even a single loop over i (O(n)) is too slow for n = 10^12.
count = 0
for i in range(1, n + 1):
    for j in range(i, n + 1, i):
        count += 1
print(count)
