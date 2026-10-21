a = int(input())
b = int(input())
k = int(input())

count = 0
for x in range(a, b + 1):
    if x % k == 0:
        count += 1

print(count)
