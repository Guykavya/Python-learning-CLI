nums = [int(x) for x in input().split()]
target = int(input())
counts = {}
for x in nums:
    counts[x] = counts.get(x, 0) + 1
pairs = []
for a in counts:
    b = target - a
    if a < b and b in counts:
        pairs.append((a, b))
    elif a == b and counts[a] >= 2:
        pairs.append((a, b))
pairs.sort()
for a, b in pairs:
    print(f"{a} + {b}")
print("Pairs:", len(pairs))
