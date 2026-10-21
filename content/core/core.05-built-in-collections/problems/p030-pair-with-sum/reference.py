nums = [int(x) for x in input().split()]
target = int(input())
first_pos = {}
for j, x in enumerate(nums, start=1):
    need = target - x
    if need in first_pos:
        print(first_pos[need], j)
        break
    if x not in first_pos:
        first_pos[x] = j
else:
    print("No pair")
