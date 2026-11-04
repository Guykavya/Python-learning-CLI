n, k = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

seen = {0: 1}       # remainder of a prefix sum -> how many prefixes so far had it (P[0] = 0)
total = 0
rem = 0
for x in a:
    rem = (rem + x) % k             # Python's % is never negative for k > 0
    total += seen.get(rem, 0)       # every earlier prefix with the same remainder ends a good subarray here
    seen[rem] = seen.get(rem, 0) + 1
print(total)
