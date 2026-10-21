n = int(input())
a = [int(x) for x in input().split()]
q = int(input())

# Correct but slow: each question copies a slice and adds it, O(n) per question.
for k in range(q):
    l, r = [int(x) for x in input().split()]
    print(sum(a[l - 1:r]))
