q = int(input())
for _ in range(q):
    n = int(input())
    count = 0
    for d in range(1, n + 1):
        if n % d == 0:
            count += 1
    print(count)
