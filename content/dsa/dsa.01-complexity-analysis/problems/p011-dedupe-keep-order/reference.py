n = int(input())
a = [int(x) for x in input().split()]

seen = set()        # fast "have I met this value?"
result = []         # keeps the order
for x in a:
    if x not in seen:
        seen.add(x)
        result.append(x)
print(len(result))
print(" ".join(str(x) for x in result))
