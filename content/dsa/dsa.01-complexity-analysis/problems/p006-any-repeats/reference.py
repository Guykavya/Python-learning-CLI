n = int(input())
a = [int(x) for x in input().split()]

seen = set()
found = False
for x in a:
    if x in seen:          # a set answers "have I seen x?" in O(1) on average
        found = True
        break
    seen.add(x)
if found:
    print("YES")
else:
    print("NO")
