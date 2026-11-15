n = int(input())
a = [int(x) for x in input().split()]

count = {}
for x in a:
    count[x] = count.get(x, 0) + 1

for value, c in count.items():
    print(value, c)
