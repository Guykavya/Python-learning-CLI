n = int(input())
a = sorted(int(x) for x in input().split())

triplets = []
for i in range(n - 2):
    if i > 0 and a[i] == a[i - 1]:
        continue                      # same first value as before: same triplets again
    l, r = i + 1, n - 1
    while l < r:
        s = a[i] + a[l] + a[r]
        if s < 0:
            l += 1
        elif s > 0:
            r -= 1
        else:
            triplets.append(f"{a[i]} {a[l]} {a[r]}")
            l += 1
            r -= 1
            while l < r and a[l] == a[l - 1]:
                l += 1                # skip copies of the middle value
print(len(triplets))
for t in triplets:
    print(t)
