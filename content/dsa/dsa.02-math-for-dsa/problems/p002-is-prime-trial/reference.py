q = int(input())
for _ in range(q):
    n = int(input())
    if n < 2:
        print("composite")
        continue
    i = 2
    prime = True
    while i * i <= n:
        if n % i == 0:
            prime = False
            break
        i += 1
    print("prime" if prime else "composite")
