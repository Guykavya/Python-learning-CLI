n, t = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

# Correct but slow: tries every pair (i, j) with i < j, in order of j and then i.
answer = "none"
found = False
for j in range(n):
    for i in range(j):
        if a[i] + a[j] == t:
            answer = f"{i + 1} {j + 1}"
            found = True
            break
    if found:
        break
print(answer)
