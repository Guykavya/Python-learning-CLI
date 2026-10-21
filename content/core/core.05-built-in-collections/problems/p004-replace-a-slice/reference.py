nums = [int(x) for x in input().split()]
i, j = [int(x) for x in input().split()]
new = [int(x) for x in input().split()]
nums[i:j] = new
print(" ".join(str(n) for n in nums) if nums else "(empty)")
