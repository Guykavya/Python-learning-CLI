n = int(input())
members = [int(x) for x in input().split()]
q = int(input())

# Correct but slow: `x in members` scans the whole list when x is missing.
for k in range(q):
    x = int(input())
    if x in members:
        print("YES")
    else:
        print("NO")
