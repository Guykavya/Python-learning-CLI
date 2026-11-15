q = int(input())
for _ in range(q):
    a, b = (int(x) for x in input().split())
    # TODO: g = gcd(a, b) with Euclid's loop, then print the lcm as an exact integer
    print(a * b)
