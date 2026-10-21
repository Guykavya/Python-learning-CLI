nums = input().split()
target = int(input())
count = 0
for i in range(len(nums)):
    for j in range(i + 1, len(nums)):
        a = int(nums[i])
        b = int(nums[j])
        if a + b == target:
            print(f"{a} + {b}")
            count += 1
print(f"Pairs: {count}")
