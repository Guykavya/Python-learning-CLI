n = int(input())

# Correct but slow: it really runs about n * n / 2 steps.
# Replace the loops with a formula that gives the same number.
count = 0
for i in range(n):
    for j in range(i + 1, n):
        count += 1
print(count)
