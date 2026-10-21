nums = [int(x) for x in input().split()]
print([n * n for n in nums if n % 2 == 0])
print([n if n >= 0 else 0 for n in nums])
print(sorted({n % 3 for n in nums}))
