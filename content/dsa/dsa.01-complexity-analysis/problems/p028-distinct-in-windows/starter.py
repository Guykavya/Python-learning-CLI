n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

# Correct but slow: each block is copied and turned into a set, O(k) per block.
answers = []
for i in range(n - k + 1):
    answers.append(len(set(a[i:i + k])))
print(" ".join(str(x) for x in answers))
