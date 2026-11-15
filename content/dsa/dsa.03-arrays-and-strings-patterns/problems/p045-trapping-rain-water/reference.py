n = int(input())
h = [int(x) for x in input().split()]

i, j = 0, n - 1
left_max = right_max = 0
total = 0
while i <= j:
    if left_max <= right_max:
        # the right side has a wall at least as high as left_max, so bar i's level is decided by left_max
        left_max = max(left_max, h[i])
        total += left_max - h[i]
        i += 1
    else:
        right_max = max(right_max, h[j])
        total += right_max - h[j]
        j -= 1
print(total)
