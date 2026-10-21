nums = [int(x) for x in input().split()]
print(tuple(nums))
print((min(nums), max(nums)))
print(tuple(n for n in nums if n % 2 == 0))
