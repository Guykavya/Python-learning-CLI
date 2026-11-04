q = int(input())
for _ in range(q):
    n, p = [int(x) for x in input().split()]
    # exponent of the prime p in n!
    print(n // p)
