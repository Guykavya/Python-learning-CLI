n, t = [int(x) for x in input().split()]
a = [int(x) for x in input().split()]

# For each position j, every earlier position holding t - a[j] makes one pair.
count_so_far = {}            # value -> how many times it appeared before the current position
pairs = 0
for x in a:
    pairs += count_so_far.get(t - x, 0)
    count_so_far[x] = count_so_far.get(x, 0) + 1
print(pairs)
