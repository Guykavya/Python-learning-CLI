n = int(input())
a = [int(x) for x in input().split()]

# Correct but slow: `x not in result` scans the result list every time.
result = []
for x in a:
    if x not in result:
        result.append(x)
print(len(result))
print(" ".join(str(x) for x in result))
