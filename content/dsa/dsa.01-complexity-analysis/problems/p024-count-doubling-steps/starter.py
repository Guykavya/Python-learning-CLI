n = int(input())

# Correct but slow: about n * log2(n) steps.
count = 0
for i in range(1, n + 1):
    j = 1
    while j <= i:
        count += 1
        j = j * 2
print(count)
